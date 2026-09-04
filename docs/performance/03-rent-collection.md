# Performance Case Study 3 — Monthly Collection Aggregation Optimization

- **Requirement ID**: `PL-134`
- **Component**: Financial Operations & Rent Collection Efficiency
- **Workload**: Heavy Multi-Table Analytical Aggregation (132,000+ Rent Charges)
- **Target Script**: [`performance/benchmarks/03_rent_collection.sql`](file:///D:/PropLedger/performance/benchmarks/03_rent_collection.sql)

---

## 1. Executive Summary

Monthly rent collection efficiency analysis aggregates billed charges against actual collections across all properties, buildings, units, and leases. Under 132,000+ historical charge records, evaluating collection metrics without covering indexes forces PostgreSQL to perform heavy `Bitmap Heap Scans` or parallel `Seq Scans` with multi-thousand block disk and cache hits.

By implementing a composite covering index on `rent_charges(billing_year, billing_month, lease_id) INCLUDE (charge_id, charge_amount, amount_paid, status)`, PostgreSQL executes an **Index Only Scan**, delivering a **79.9% reduction in shared buffer reads** and a **21.5% speedup**.

---

## 2. Baseline Architecture & Bottleneck Analysis

### 2.1 The Baseline Workload

```sql
SELECT 
    rc.billing_year,
    rc.billing_month,
    p.property_id,
    p.name AS property_name,
    COUNT(rc.charge_id) AS total_billed_charges,
    SUM(rc.charge_amount) AS total_amount_billed,
    SUM(rc.amount_paid) AS total_amount_collected,
    SUM(rc.charge_amount - rc.amount_paid) AS total_outstanding,
    ROUND(SUM(rc.amount_paid) / NULLIF(SUM(rc.charge_amount), 0) * 100, 2) AS collection_rate_pct,
    COUNT(CASE WHEN rc.status = 'Paid' THEN 1 END) AS fully_paid_count,
    COUNT(CASE WHEN rc.status = 'PartiallyPaid' THEN 1 END) AS partial_count,
    COUNT(CASE WHEN rc.status = 'Overdue' THEN 1 END) AS overdue_count
FROM rent_charges rc
JOIN leases l ON l.lease_id = rc.lease_id
JOIN units u ON u.unit_id = l.unit_id
JOIN buildings b ON b.building_id = u.building_id
JOIN properties p ON p.property_id = b.property_id
WHERE rc.billing_year = 2025
GROUP BY rc.billing_year, rc.billing_month, p.property_id, p.name
ORDER BY rc.billing_year DESC, rc.billing_month DESC, total_amount_billed DESC;
```

### 2.2 Baseline Plan Bottleneck (`03_rent_collection_before.txt`)
```
-> Bitmap Heap Scan on public.rent_charges rc (cost=429.39..4414.80 rows=30593)
     Recheck Cond: (rc.billing_year = 2025)
     Heap Blocks: exact=1716
     Buffers: shared hit=1753
     -> Bitmap Index Scan on idx_rent_charges_period
```
- **Heap Table Reads**: The Phase 1 index `idx_rent_charges_period(billing_year, billing_month)` only indexed the period, requiring PostgreSQL to read 1,716 table heap blocks to obtain `charge_id`, `charge_amount`, `amount_paid`, and `status`.

---

## 3. Engineering Solution: Covering Composite Index

```sql
CREATE INDEX IF NOT EXISTS idx_rent_charges_year_month_cov 
ON rent_charges(billing_year, billing_month, lease_id) 
INCLUDE (charge_id, charge_amount, amount_paid, status);
```

### Design Rationale:
- **Leading Equality Keys**: `billing_year, billing_month` enables direct B-Tree range scans.
- **Join Key Integration**: `lease_id` is retained in the index tree to streamline joins to `leases(lease_id)`.
- **Covered Attributes**: All arithmetic aggregates (`SUM(charge_amount)`, `SUM(amount_paid)`, `COUNT(status)`) are resolved directly from the index payload.

---

## 4. Optimized Plan Analysis (`03_rent_collection_after.txt`)

```
-> Index Only Scan Backward using idx_rent_charges_year_month_cov on rent_charges rc
     Index Cond: (billing_year = 2025)
     Heap Fetches: 0
     Buffers: shared hit=1 read=251
```

- **Heap Fetches Dropped to 0**: The table heap is bypassed completely.
- **Buffer Pages**: The entire scan on `rent_charges` dropped from **1,753 blocks** to **252 blocks**.
- **Estimated Cost**: Overall query cost decreased from **6,596.46** to **3,737.46** (**43.3% reduction**).

---

## 5. Metrics & Verification Summary

| Metric | Before Optimization | After Optimization | Impact |
|---|---|---|---|
| **Scan Type on `rent_charges`** | `Bitmap Heap Scan` (1716 heap blocks) | `Index Only Scan` (0 heap blocks) | **100% Heap Access Eliminated** |
| **Total Query Shared Buffers** | 13,198 blocks | 2,654 blocks | **79.9% I/O Saved (-10,544 blocks)** |
| **Execution Time** | 58.41 ms | 45.88 ms | **21.5% Faster** |
| **Plan Cost** | 6,596.46 | 3,737.46 | **43.3% Cost Reduction** |

---

## 6. Architectural Takeaway

For analytical queries aggregating millions of transactions across grouping dimensions, covering indexes that embed join foreign keys and aggregation operands into the index payload eliminate random disk I/O, converting multi-second sequential scans into sub-50ms Index-Only Scans.
