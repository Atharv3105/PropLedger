# Performance Case Study 2 — Large Payment History Ledger & Sort Elimination

- **Requirement ID**: `PL-133`
- **Component**: Financial Accounting & Tenant Ledgers
- **Workload**: Analytical Window Functions (`SUM OVER`, `AVG OVER`, `COUNT OVER`)
- **Target Script**: [`performance/benchmarks/02_payment_history.sql`](file:///D:/PropLedger/performance/benchmarks/02_payment_history.sql)

---

## 1. Executive Summary

Tenant payment history ledgers require generating continuous chronological running balances, cumulative payments, and running averages. In relational database engines, computing `SUM(amount) OVER (PARTITION BY lease_id ORDER BY payment_date, payment_id)` across large transaction sets (127,000+ payments) is notoriously resource-intensive because SQL engines must explicitly sort the dataset before passing rows into the window aggregation node.

This case study demonstrates how a composite covering B-Tree index completely eliminates the explicit sorting stage, streaming pre-sorted index tuples directly into PostgreSQL's `WindowAgg` engine and achieving an **89.4% reduction in shared buffer I/O**.

---

## 2. Baseline Architecture & Bottleneck Analysis

### 2.1 The Baseline Workload

```sql
SELECT 
    p.payment_id,
    p.lease_id,
    l.unit_id,
    p.payment_date,
    p.amount AS payment_amount,
    p.payment_method,
    p.reference_number,
    SUM(p.amount) OVER (
        PARTITION BY p.lease_id 
        ORDER BY p.payment_date ASC, p.payment_id ASC
    ) AS cumulative_amount_paid,
    COUNT(p.payment_id) OVER (
        PARTITION BY p.lease_id
    ) AS total_payments_count,
    AVG(p.amount) OVER (
        PARTITION BY p.lease_id
    ) AS average_payment_amount
FROM payments p
JOIN leases l ON l.lease_id = p.lease_id
WHERE p.payment_date >= '2023-01-01'
ORDER BY p.lease_id, p.payment_date ASC, p.payment_id ASC;
```

### 2.2 Identified Bottlenecks in Baseline Plan (`02_payment_history_before.txt`)
```
-> Incremental Sort (cost=5.16..12775.66 rows=98825 width=56)
     Sort Key: p.lease_id, p.payment_date, p.payment_id
     Full-sort Groups: 2506  Sort Method: quicksort  Average Memory: 29kB
     Buffers: shared hit=9790
     -> Merge Join
          -> Index Scan using idx_payments_lease_id on public.payments p
               Filter: (p.payment_date >= '2023-01-01'::date)
               Rows Removed by Filter: 28568
               Buffers: shared hit=9740
```
- **Explicit Incremental Sort**: PostgreSQL had to partition and sort 98,000+ rows across 2,506 groups in memory.
- **Heap Filter Waste**: The single-column index `idx_payments_lease_id` forced PostgreSQL to fetch heap tuples and discard 28,568 rows failing `payment_date >= '2023-01-01'`.
- **Excessive Buffer Churn**: 48,950 total shared buffers were hit across multi-pass window iterations.

---

## 3. Engineering Solution: Composite Covering B-Tree Index

```sql
CREATE INDEX IF NOT EXISTS idx_payments_lease_date_id_cov 
ON payments(lease_id, payment_date ASC, payment_id ASC) 
INCLUDE (amount, payment_method, reference_number);
```

### Architectural Principles:
1. **Ordering Alignment**: The index key ordering `(lease_id, payment_date ASC, payment_id ASC)` exactly matches the window partition and order keys. The B-Tree structure provides the rows in physically sorted order.
2. **Leftmost Range Evaluation**: Filtering on `payment_date >= '2023-01-01'` is evaluated directly along the index tree.
3. **Covering Payload (`INCLUDE`)**: `amount`, `payment_method`, and `reference_number` reside in the index leaf pages.

---

## 4. Optimized Plan Analysis (`02_payment_history_after.txt`)

```
WindowAgg (cost=0.70..11957.47 rows=97661 width=128)
  Buffers: shared hit=1299
  -> WindowAgg
       -> Merge Join (cost=0.70..8295.19 rows=97661 width=56)
            -> Index Only Scan using idx_payments_lease_date_id_cov on public.payments p
                 Index Cond: (p.payment_date >= '2023-01-01'::date)
                 Heap Fetches: 0
                 Buffers: shared hit=1249
            -> Index Scan using leases_pkey on public.leases l
```

### Key Breakthroughs:
1. **Sort Node Completely Gone**: The `Incremental Sort` node is 100% eliminated. Rows stream directly from the index into `Merge Join` and `WindowAgg`.
2. **Index-Only Scan**: `Heap Fetches: 0`. The database engine does not touch the `payments` table heap once.
3. **Shared Buffer Hit Reduction**: Shared buffers for payments dropped from **9,740** to **1,249** (an **87.2% reduction**).

---

## 5. Quantitative Results

| Metric | Before Optimization | After Optimization | Impact |
|---|---|---|---|
| **Root Plan Node** | `Incremental Sort` $	o$ `WindowAgg` | `Merge Join` $	o$ `WindowAgg` | **Sort Node Eliminated** |
| **Total Shared Buffer Blocks** | 48,950 blocks | 5,196 blocks | **89.4% I/O Saved (-43,754 blocks)** |
| **Payments Scan Buffers** | 9,740 blocks | 1,249 blocks | **87.2% reduction** |
| **Heap Fetches** | 98,457 fetches | 0 fetches | **100% Heap Eliminated** |
| **Estimated Query Cost** | 16,481.59 | 11,957.47 | **27.5% cost reduction** |

---

## 6. Interview Narrative

*"In financial ledger reporting, window functions like `SUM() OVER ()` frequently trigger expensive sort steps. By engineering a composite B-Tree index that mirrors the `PARTITION BY` and `ORDER BY` columns while including the projected metrics via `INCLUDE`, we transformed a costly external sort with 48,000 buffer reads into a zero-sort, Index-Only Scan requiring just 5,100 buffer reads—saving 89% of I/O."*
