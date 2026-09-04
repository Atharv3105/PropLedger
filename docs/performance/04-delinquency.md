# Performance Case Study 4 — Delinquency Aging Under Heavy Volume (Partial Indexing)

- **Requirement ID**: `PL-135`
- **Component**: Risk Management & Collections Pipeline
- **Workload**: Multi-Bucket Arrears Aging (Current, 1-30, 31-60, 61-90, >90 Days)
- **Target Script**: [`performance/benchmarks/04_delinquency.sql`](file:///D:/PropLedger/performance/benchmarks/04_delinquency.sql)

---

## 1. Executive Summary

Delinquency aging reports identify high-risk tenancies with overdue balances, grouping unpaid balances into chronological buckets (`1-30`, `31-60`, `61-90`, and `>90` days past due). In a healthy property portfolio, **over 90% of rent charges are fully paid on time**. Consequently, full table scans or general B-Tree indexes waste 90% of their traversal effort evaluating irrelevant paid records.

This case study demonstrates the power of a **Partial (Filtered) Covering Index** that indexes strictly delinquent charges (`status IN ('Pending', 'PartiallyPaid', 'Overdue')`), resulting in a **39.2% execution time improvement (1.6x speedup)** and an **80.8% reduction in buffer reads**.

---

## 2. Baseline Architecture & Bottleneck Analysis

### 2.1 The Baseline Workload

```sql
SELECT 
    p.property_id,
    p.name AS property_name,
    l.lease_id,
    t.first_name || ' ' || t.last_name AS tenant_name,
    u.unit_number,
    SUM(rc.charge_amount - rc.amount_paid) AS total_delinquent_balance,
    SUM(CASE WHEN (CURRENT_DATE - rc.due_date) BETWEEN 1 AND 30 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END) AS aging_1_30_days,
    SUM(CASE WHEN (CURRENT_DATE - rc.due_date) BETWEEN 31 AND 60 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END) AS aging_31_60_days,
    SUM(CASE WHEN (CURRENT_DATE - rc.due_date) BETWEEN 61 AND 90 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END) AS aging_61_90_days,
    SUM(CASE WHEN (CURRENT_DATE - rc.due_date) > 90 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END) AS aging_over_90_days,
    MAX(CURRENT_DATE - rc.due_date) AS max_days_past_due
FROM rent_charges rc
JOIN leases l ON l.lease_id = rc.lease_id
JOIN units u ON u.unit_id = l.unit_id
JOIN buildings b ON b.building_id = u.building_id
JOIN properties p ON p.property_id = b.property_id
LEFT JOIN lease_tenants lt ON lt.lease_id = l.lease_id AND lt.is_primary = TRUE
LEFT JOIN tenants t ON t.tenant_id = lt.tenant_id
WHERE rc.status IN ('Pending', 'PartiallyPaid', 'Overdue')
  AND rc.charge_amount > rc.amount_paid
  AND rc.due_date < CURRENT_DATE
GROUP BY p.property_id, p.name, l.lease_id, t.first_name, t.last_name, u.unit_number
HAVING SUM(rc.charge_amount - rc.amount_paid) > 0
ORDER BY total_delinquent_balance DESC, max_days_past_due DESC;
```

### 2.2 Baseline Bottlenecks (`04_delinquency_before.txt`)
- **Bitmap Heap Scan over 1,330 blocks**: Reading unindexed columns (`charge_amount`, `amount_paid`, `due_date`) from heap pages.
- **High Overall Plan Cost**: Cost `5,193.78..5,197.05` across 12,370 shared buffers.

---

## 3. Engineering Solution: Partial Filtered Index

```sql
CREATE INDEX IF NOT EXISTS idx_rent_charges_delinquent_partial 
ON rent_charges(lease_id, due_date) 
INCLUDE (charge_amount, amount_paid, status) 
WHERE status IN ('Pending', 'PartiallyPaid', 'Overdue');
```

### Why a Partial Index Excels:
1. **Size Efficiency**: Instead of indexing all 132,245 charges, the index stores only the ~12,000 delinquent charges—**a 91% reduction in index size**.
2. **Zero Write Overhead for Paid Charges**: When on-time tenants pay their rent, this index is never modified, completely shielding the database from write amplification.
3. **Index-Only Execution**: Including `charge_amount`, `amount_paid`, and `status` in the payload allows PostgreSQL to satisfy all aging calculations directly from index pages.

---

## 4. Optimized Plan Analysis (`04_delinquency_after.txt`)

```
-> Index Only Scan using idx_rent_charges_delinquent_partial on public.rent_charges rc
     Index Cond: (rc.due_date < CURRENT_DATE)
     Filter: (rc.charge_amount > rc.amount_paid)
     Heap Fetches: 0
     Buffers: shared hit=82
```

- **Buffers on `rent_charges` dropped from 1,346 to 82**: A **93.9% buffer I/O reduction** on the target table!
- **Total Plan Cost**: Dropped from **5,197.05** to **1,755.78** (a **66.2% cost reduction**).
- **Execution Time**: Dropped from **34.81 ms** to **21.15 ms** (**39.2% faster / 1.6x speedup**).

---

## 5. Quantitative Results

| Metric | Baseline | Optimized (Partial Index) | Improvement |
|---|---|---|---|
| **Index Size vs Full Index** | 100% (132k rows) | ~9% (12k rows) | **91% Smaller Index Footprint** |
| **Buffers on `rent_charges`** | 1,346 blocks | 82 blocks | **93.9% Table Buffer Reduction** |
| **Total Query Shared Buffers** | 12,370 blocks | 2,377 blocks | **80.8% Total I/O Saved (-9,993 blocks)** |
| **Execution Time** | 34.81 ms | 21.15 ms | **1.6x Speedup (39.2% faster)** |
| **Query Cost** | 5,197.05 | 1,755.78 | **66.2% Cost Reduction** |

---

## 6. Interview Narrative

*"In collections operations, querying unpaid charges is a classic candidate for partial indexing. Since 90% of our 132,000 charges are fully paid, indexing the whole table wastes disk and slows down writes. By creating a partial index with `WHERE status IN ('Pending', 'PartiallyPaid', 'Overdue')`, we reduced index footprint by 91%, eliminated 94% of table buffer reads, and achieved a 1.6x speedup with zero write penalty for on-time payments."*\n