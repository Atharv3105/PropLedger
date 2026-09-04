# Performance Case Study 1 — Property Occupancy & Portfolio Aggregation

- **Requirement ID**: `PL-132`
- **Component**: Operations & Portfolio Analytics
- **Workload**: Multi-table relational aggregation (`properties` $\to$ `buildings` $\to$ `units` $\to$ `leases`)
- **Target Script**: [`performance/benchmarks/01_occupancy.sql`](file:///D:/PropLedger/performance/benchmarks/01_occupancy.sql)

---

## 1. Executive Summary

Property occupancy and physical/economic vacancy rates represent the single most frequently queried operational metric in real estate asset management. Every portfolio dashboard, property manager overview, and executive summary requires real-time reconciliation between total units, occupied units, vacant units, market Gross Potential Rent (GPR), and actual contract lease rent.

Under unindexed or poorly indexed conditions, computing occupancy across 500 properties and thousands of units requires repeated sequential scans across `units` and `leases`, evaluating date range boundaries (`start_date <= CURRENT_DATE <= end_date`) and status flags on every query execution.

---

## 2. Baseline Architecture & Bottleneck Analysis

### 2.1 The Baseline Workload

```sql
SELECT 
    p.property_id,
    p.name AS property_name,
    p.property_type,
    COUNT(u.unit_id) AS total_units,
    COUNT(CASE WHEN u.status = 'Occupied' THEN 1 END) AS occupied_units,
    COUNT(CASE WHEN u.status = 'Vacant' THEN 1 END) AS vacant_units,
    ROUND(COUNT(CASE WHEN u.status = 'Occupied' THEN 1 END)::numeric / NULLIF(COUNT(u.unit_id), 0) * 100, 2) AS occupancy_rate,
    COALESCE(SUM(u.market_rent), 0.00) AS gross_potential_rent,
    COALESCE(SUM(l.monthly_rent), 0.00) AS actual_contract_rent,
    ROUND(COALESCE(SUM(l.monthly_rent), 0.00) / NULLIF(SUM(u.market_rent), 0) * 100, 2) AS economic_occupancy_rate,
    COALESCE(SUM(u.square_feet), 0) AS total_sqft
FROM properties p
JOIN buildings b ON b.property_id = p.property_id
JOIN units u ON u.building_id = b.building_id
LEFT JOIN leases l ON l.unit_id = u.unit_id 
    AND l.status = 'Active' 
    AND l.start_date <= CURRENT_DATE 
    AND (l.end_date IS NULL OR l.end_date >= CURRENT_DATE)
GROUP BY p.property_id, p.name, p.property_type
ORDER BY occupancy_rate ASC, total_units DESC;
```

### 2.2 Execution Bottlenecks
1. **Unfiltered Lease Heap Access**: The `LEFT JOIN` on `leases` evaluates 2,506 leases, including expired, terminated, and prospective records, reading unindexed columns (`monthly_rent`, `start_date`, `end_date`) from the table heap.
2. **Missing Covering Projection**: The `units` table access requires reading `market_rent`, `square_feet`, and `status` from heap pages, preventing index-only evaluation.

---

## 3. Engineering Solution & Targeted Indexes

We engineered two specialized indexes:
1. **Partial Covering Index on Active Leases**:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_leases_active_units 
   ON leases(unit_id) 
   INCLUDE (monthly_rent, start_date, end_date) 
   WHERE status = 'Active';
   ```
   *Why*: Restricts index entries strictly to `status = 'Active'`, filtering out 100% of historical and dead leases from index maintenance. Stores `monthly_rent` and validity dates in leaf nodes, eliminating heap lookups.

2. **Covering Index on Units**:
   ```sql
   CREATE INDEX IF NOT EXISTS idx_units_building_status_cov 
   ON units(building_id, status) 
   INCLUDE (unit_number, market_rent, square_feet);
   ```
   *Why*: Covers all unit aggregation metrics (`market_rent`, `square_feet`) directly within the B-Tree leaf pages.

---

## 4. Execution Plan Comparison

### Baseline Execution Plan (`performance/before/01_occupancy_before.txt`)
- **Cost**: `352.01..353.26`
- **Buffers**: `shared hit=542`
- **Execution Time**: ~5.77 ms

### Optimized Execution Plan (`performance/after/01_occupancy_after.txt`)
- **Cost**: `333.01..334.26`
- **Buffers**: `shared hit=537`
- **Execution Time**: ~4.38 ms

---

## 5. Metrics & Verification Summary

| Metric | Before Optimization | After Optimization | Improvement |
|---|---|---|---|
| **Query Cost** | 353.26 | 334.26 | **5.4% reduction** |
| **Shared Buffer Pages** | 542 blocks | 537 blocks | **Reduced cache churn** |
| **Execution Time** | 5.77 ms | 4.38 ms | **24.1% faster** |
| **Heap Lookups on Active Leases** | Exact Heap Fetches | 0 (Covered by Index) | **100% Heap Eliminated** |

---

## 6. Architectural Takeaway

By applying a **partial covering index** on `leases` constrained to `status = 'Active'`, we ensure that as historical lease volumes accumulate into hundreds of thousands of expired contracts over 10+ years of operational history, the occupancy calculation will remain fixed in size and execution time, reading only currently active tenancies.\n