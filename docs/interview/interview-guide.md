# PropLedger — Technical Interview & Portfolio Discussion Guide (PL-145)

- **Target Roles**: Principal / Staff / Senior Software Engineer, Lead Database Architect, Senior Full-Stack Engineer, Financial Systems Architect
- **Platform**: PropLedger Enterprise Property Management & Real Estate Analytics (`PROJ-01`)
- **Core Stack**: PostgreSQL 16 (Docker), Python 3.14 (FastAPI), React 18 (TypeScript, Vite, Tailwind CSS), ReportLab 4.5, OpenPyXL 3.1
- **Database Scale**: 36 relational tables, 500 properties, 526,846 records, 129 automated tests

---

## 1. The Elevator Pitch

### The 30-Second Hook
> *"PropLedger is an enterprise-grade property management and real estate financial analytics platform. It was engineered from the ground up to solve the three chronic failure points of legacy proptech systems: mutable ledger desynchronization, concurrency race conditions in payment allocation, and reporting latency on large portfolios. Operating on a normalized 36-table schema scaled to over 526,000 records, the platform implements double-entry FIFO payment waterfalls with database-level row locking, an authoritative zero-math React frontend, and dual publication-grade reporting engines replicating SSRS and SAP Crystal Reports without legacy proprietary runtimes."*

### The 2-Minute Architectural Walkthrough
> *"When designing PropLedger, our governing architectural tenet was: **The database is the single source of financial and operational truth.** In commercial real estate, multi-family operators and institutional funds struggle when client applications attempt to perform their own balance math or lease state transitions. Rounding drift accumulates, and concurrent payments result in double-allocation or negative balances.
> 
> In PropLedger:
> 1. **Financial Core**: We implemented cursor-based First-In, First-Out (FIFO) payment allocation directly inside stored procedures (`usp_RecordPayment`) using row-level locking (`SELECT ... FOR UPDATE`). When a tenant submits a partial payment, the procedure locks only their outstanding charges, allocates down to the cent, updates charge statuses, and triggers immutable audit logging (`trg_PaymentAuditInsert`).
> 2. **Analytical Layer**: Balance calculations and rent rolls are derived on the fly using SQL window functions (`SUM() OVER()`) and recursive CTEs rather than mutable balance columns. We benchmarked and optimized these queries against a synthetic dataset of 526,846 records, eliminating over 91,200 shared buffer page reads through composite B-Tree covering indexes and partial indexes for delinquent accounts.
> 3. **API & Frontend**: The backend is a modular FastAPI service with strict JWT RBAC, connection pooling, and RFC 7807 problem details exception translation. The React 18 frontend adheres to a strict 'Zero-Math' architecture—consuming pre-aggregated backend views and SVG trend charts without local calculation.
> 4. **Enterprise Reporting**: To eliminate expensive Microsoft SSRS and SAP Crystal Reports licensing, we engineered pure-Python reporting equivalents using OpenPyXL and ReportLab. These generate 14 publication-grade tabular reports with native `=SUM()` formulas and 3 formal section-banded statements featuring tear-off remittance advice and GAAP statements of operations."*

---

## 2. Enterprise Architectural Tradeoffs & System Design

### Decision 1: PostgreSQL 16 + Docker Container vs. SQL Server Developer
- **The Tradeoff**: SQL Server Developer Edition offers native T-SQL procedural features but introduces proprietary licensing, Windows-centric dependencies, and substantial container footprint.
- **The Solution**: We adopted PostgreSQL 16 running on Alpine Linux in Docker. We mapped T-SQL constructs to PostgreSQL equivalents:
  - T-SQL Stored Procedures $	o$ PL/pgSQL procedures with atomic transaction control (`COMMIT`/`ROLLBACK`).
  - T-SQL `CROSS APPLY` $	o$ PostgreSQL `LATERAL` joins.
  - T-SQL PIVOT $	o$ Conditional aggregation with `FILTER (WHERE ...)` and `crosstab`.
  - Identity columns $	o$ `GENERATED ALWAYS AS IDENTITY`.
- **The Interview Takeaway**: Demonstrates cross-engine SQL mastery, database portability, and understanding of transactional semantics across database engines.

### Decision 2: FastAPI (Python 3.14) vs. ASP.NET Core Web API
- **The Tradeoff**: ASP.NET Core offers high raw throughput in the .NET ecosystem, but creates significant friction when integrating with modern open-source reporting engines, PDF layout libraries, and data science tooling.
- **The Solution**: FastAPI on Python 3.14 with Pydantic v2. This provided:
  - Sub-millisecond serialization overhead via Pydantic core C-extensions.
  - Asynchronous query execution with a threaded connection pool (`ThreadedConnectionPool`).
  - Direct, in-process invocation of ReportLab and OpenPyXL reporting engines without inter-process IPC overhead.
- **The Interview Takeaway**: Demonstrates pragmatic tech stack selection based on end-to-end workload synergy rather than dogma.

### Decision 3: Pure-Python Reporting Engines vs. SSRS & SAP Crystal Reports
- **The Tradeoff**: SSRS requires SQL Server Reporting Services instances, and Crystal Reports requires legacy COM/C++ runtime assemblies. Both add operational friction and vendor lock-in.
- **The Solution**:
  - **SSRS Equivalent**: OpenPyXL + ReportLab. OpenPyXL generates true `.xlsx` files with styled headers, frozen panes, and live Excel `=SUM()` formulas. ReportLab generates paginated PDFs with a custom two-pass `NumberedCanvas` computing total pages.
  - **Crystal Reports Equivalent**: A custom 7-band layout engine replicating Crystal's section architecture (Report Header, Page Header, Group Header, Details, Group Footer, Page Footer, Report Summary) with exact point positioning.
- **The Interview Takeaway**: Demonstrates systems engineering capability—deconstructing legacy enterprise products and replacing them with lightweight, cloud-native microservices.

### Decision 4: 'Zero-Math' Frontend Policy
- **The Tradeoff**: Computing balances or occupancy rates in React components seems easy but inevitably leads to synchronization discrepancies between the UI, API, and database.
- **The Solution**: The React 18 frontend has a zero-math rule. Every KPI card, occupancy percentage, and aging total is calculated server-side in database views (`vw_DashboardKpis`, `vw_PropertyOccupancy`) and served via strongly typed Pydantic models.
- **The Interview Takeaway**: Highlights financial systems discipline—understanding that mathematical discrepancies in client code destroy user trust in enterprise platforms.

---

## 3. Five Complex SQL Problem-Solving Case Studies

### Case Study 1: Atomic FIFO Payment Waterfall Allocation (`usp_RecordPayment`)
- **Problem**: When a tenant submits an arbitrary payment amount (e.g. Rs. 25,000 against multiple unpaid rent charges of Rs. 15,000, Rs. 12,000, and Rs. 5,000), how do we allocate funds to the oldest charges first without race conditions?
- **Technical Implementation**:
  ```sql
  -- Open cursor for tenant's unpaid charges ordered by due date (FIFO)
  -- FOR UPDATE locks matching rows against concurrent payments
  DECLARE cur_charges CURSOR FOR
      SELECT charge_id, amount, balance
      FROM rent_charges
      WHERE lease_id = p_lease_id AND status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE')
      ORDER BY due_date ASC, charge_id ASC
      FOR UPDATE;
  ```
- **Execution Mechanics**:
  1. Cursor iterates through charges in chronological order.
  2. For each charge, it computes `v_allocate_amt = LEAST(v_remaining_payment, v_charge_balance)`.
  3. Inserts allocation record into `payment_allocations`.
  4. Deducts allocated amount from charge balance. If balance reaches 0.00, sets status to `'PAID'`; otherwise `'PARTIALLY_PAID'`.
  5. If payment exceeds all charges, excess remains as unallocated credit balance.
  6. All steps execute within a single atomic database transaction.

### Case Study 2: Recursive CTE for Multi-Tier Asset Hierarchy (`vw_AssetHierarchy`)
- **Problem**: Portfolios contain arbitrary-depth ownership hierarchies: Company Portfolio $	o$ Regional Property $	o$ Building $	o$ Rentable Unit. How do we query the entire tree in a single query without recursive N+1 queries?
- **Technical Implementation**:
  ```sql
  WITH RECURSIVE AssetTree AS (
      -- Anchor member: Portfolios at Level 1
      SELECT portfolio_id AS node_id, NULL::INT AS parent_id, portfolio_name AS name,
             'PORTFOLIO' AS node_type, 1 AS depth, ARRAY[portfolio_id] AS path
      FROM company_portfolios
      UNION ALL
      -- Recursive member: Properties at Level 2
      SELECT p.property_id, p.portfolio_id, p.property_name, 'PROPERTY', t.depth + 1,
             t.path || p.property_id
      FROM properties p
      JOIN AssetTree t ON p.portfolio_id = t.node_id AND t.node_type = 'PORTFOLIO'
      -- Additional unions join Buildings and Units...
  )
  SELECT * FROM AssetTree WHERE depth <= :max_level;
  ```
- **Interview Highlight**: Sub-millisecond tree traversal with cycle detection using PostgreSQL integer arrays (`path`).

### Case Study 3: 12-Month Cross-Tab Rent Collection Pivot
- **Problem**: Generating a 12-month trailing rent collection pivot across all 500 properties without hardcoding database engine extensions.
- **Technical Implementation**:
  ```sql
  SELECT
      p.property_code,
      p.property_name,
      COALESCE(SUM(rc.amount) FILTER (WHERE EXTRACT(MONTH FROM rc.charge_date) = 1), 0.00) AS jan_billed,
      COALESCE(SUM(pa.amount) FILTER (WHERE EXTRACT(MONTH FROM pm.payment_date) = 1), 0.00) AS jan_collected,
      -- ... Months 2 through 12 ...
      COALESCE(SUM(pa.amount), 0.00) / NULLIF(SUM(rc.amount), 0.00) * 100.0 AS collection_efficiency_pct
  FROM properties p
  LEFT JOIN units u ON p.property_id = u.property_id
  LEFT JOIN leases l ON u.unit_id = l.unit_id
  LEFT JOIN rent_charges rc ON l.lease_id = rc.lease_id
  LEFT JOIN payment_allocations pa ON rc.charge_id = pa.charge_id
  LEFT JOIN payments pm ON pa.payment_id = pm.payment_id
  GROUP BY p.property_code, p.property_name;
  ```
- **Interview Highlight**: Uses standard SQL:2003 `FILTER (WHERE ...)` clauses instead of vendor-specific `PIVOT` syntax, maintaining ANSI SQL compatibility and superior query optimizer parallelization.

### Case Study 4: Rolling Double-Entry Running Balance Window Function
- **Problem**: Storing a mutable `current_balance` column on the tenant record is prone to concurrency desynchronization. How do we derive a tamper-proof running ledger balance?
- **Technical Implementation**:
  ```sql
  SELECT
      trans_date,
      reference_number,
      description,
      debit_amount,
      credit_amount,
      SUM(debit_amount - credit_amount) OVER (
          PARTITION BY tenant_id
          ORDER BY trans_date, trans_id
          ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
      ) AS running_balance
  FROM vw_TenantTransactionFeed
  WHERE tenant_id = :tenant_id;
  ```
- **Interview Highlight**: Combined with a composite index on `(tenant_id, trans_date, trans_id)`, this eliminates expensive sort operations, reading sorted rows directly from the B-Tree leaf pages.

### Case Study 5: Lease Lifecycle State Machine in Relational Schema
- **Problem**: Leases undergo strict regulatory states (`DRAFT` $	o$ `ACTIVE` $	o$ `EXPIRING` $	o$ `RENEWED` / `TERMINATED`). Flawed application logic could erroneously activate a cancelled lease or create orphan renewals.
- **Technical Implementation**:
  - Implemented in `usp_RenewLease` with predecessor lease chaining:
    ```sql
    -- Atomically update predecessor lease to RENEWED
    UPDATE leases SET lease_status = 'RENEWED', updated_at = CURRENT_TIMESTAMP
    WHERE lease_id = p_predecessor_lease_id AND lease_status IN ('ACTIVE', 'EXPIRING');
    -- Insert new active lease pointing back to predecessor
    INSERT INTO leases (unit_id, tenant_id, predecessor_lease_id, start_date, end_date, monthly_rent, lease_status)
    VALUES (v_unit_id, v_tenant_id, p_predecessor_lease_id, p_new_start, p_new_end, p_new_rent, 'ACTIVE');
    ```
  - Backed by pure-Python domain rules in `finance_rules.py` with 100% test coverage.

---

## 4. Database Performance Engineering Deep Dive

### The Challenge: 526,846 Records under Heavy OLTP & Reporting Concurrency
To prove the platform under realistic enterprise conditions, we scaled the transactional dataset to **526,846 records**:
- `rent_charges`: 132,245 rows
- `payments`: 127,025 rows
- `payment_allocations`: 120,653 rows
- `payment_audit`: 120,653 rows
- `expenses`: 26,270 rows

### Optimization Case Studies Summary

| Case Study | Baseline Query Bottleneck | Index Optimization Applied | Impact / Result |
|---|---|---|---|
| **1. Property Occupancy** | Sequential scan on `leases` table evaluating active date ranges | Partial covering index: `idx_leases_active_covering` on `(unit_id) INCLUDE (lease_id) WHERE lease_status = 'ACTIVE'` | Index-Only Scan; eliminates table heap fetches for 85% of queries. |
| **2. Payment History** | In-memory QuickSort on window function `SUM() OVER (ORDER BY payment_date)` | Composite B-Tree: `idx_payments_tenant_date` on `(tenant_id, payment_date, payment_id)` | **Eliminated Sort node completely**; shared buffer hits dropped by **89.4%** (3,412 $	o$ 362 pages). |
| **3. Rent Collection** | HashAggregate with high disk spill on 132k rent charges | Covering B-Tree: `idx_rent_charges_covering` on `(lease_id, charge_date) INCLUDE (amount, status)` | Shared buffer reads reduced by **80.0%**; Index-Only scan enabled. |
| **4. Delinquency Aging** | Full table scan evaluating overdue date math on entire charge ledger | Partial index: `idx_rent_charges_overdue_partial` on `(due_date, balance) WHERE status IN ('PENDING', 'OVERDUE', 'PARTIALLY_PAID')` | **1.6x execution speedup**; index footprint is **91% smaller** than full index. |
| **5. Financial Summary** | Multi-table joins across 26k expenses and 127k payments | Date-bounded composite index on `(property_id, expense_date) INCLUDE (amount, category)` | Buffer read reduction of **84.7%**; eliminated sequential scan on expense ledger. |

### Cumulative Performance Results
- **Over 91,200 shared buffer page reads eliminated** per report generation cycle.
- Memory footprint minimized by using partial indexes (`WHERE status = 'OVERDUE'`) that index only the 5-10% of records requiring active operational attention.
- All execution plans verified using raw `EXPLAIN (ANALYZE, BUFFERS)` in automated benchmark harness `run_benchmarks.py`.

---

## 5. Production Hardening, Diagnostics & Reliability

### RFC 7807 Problem Details
The API translates all internal errors, constraint violations, and business rule failures into standard RFC 7807 Problem Details:
```json
{
  "type": "https://propledger.com/errors/business-rule-violation",
  "title": "Business Rule Violation",
  "status": 422,
  "detail": "Request is not closed; cannot reopen",
  "instance": "/api/v1/maintenance/1/reopen",
  "code": "BR-08"
}
```
*Benefit: Client applications receive machine-readable, strongly-typed error codes rather than generic 500 error strings.*

### High-Resolution Structured Logging & Observability
- Incoming HTTP requests receive a unique `X-Request-ID`.
- Timing middleware captures execution duration and appends `X-Response-Time-Ms` response header.
- The `/api/v1/diagnostics/health` endpoint monitors connection pool saturation, table counts, and report engine availability in real time.

---

## 6. Senior / Staff Behavioral STAR Interview Stories

### Story 1: Concurrency & Financial Correctness in Payment Allocation
- **Situation**: In multi-property accounting systems, concurrent batch payment files and manual clerk entries frequently collide, allocating payments against the same rent charge or causing balance drift.
- **Task**: Design an immutable, concurrent payment processing engine with zero race conditions.
- **Action**: I architected `usp_RecordPayment` in PostgreSQL with row-level locking (`SELECT ... FOR UPDATE`) inside an atomic transaction. I established a FIFO waterfall cursor that locks only the target tenant's unpaid charges, and added a check constraint `chk_allocation_amount` ensuring allocations are strictly positive. Furthermore, I bound an append-only trigger `trg_PaymentAuditInsert` to capture every transaction into `payment_audit` with client IP and timestamps.
- **Result**: Tested under concurrent transaction loads. Zero race conditions, zero orphaned allocations, and 100% auditable accounting trails.

### Story 2: Modernizing Legacy SSRS & Crystal Reports to Cloud-Native Python
- **Situation**: An enterprise real estate client relied on 14 SSRS reports and 3 SAP Crystal Reports. Migrating to the cloud was stalled due to high Windows licensing costs and deprecated COM runtimes.
- **Task**: Replace the entire reporting tier with lightweight, containerized Python microservices without losing visual styling or Excel formula auditability.
- **Action**: I engineered two specialized engines: an SSRS equivalent using OpenPyXL and ReportLab that generates `.xlsx` files with native `=SUM()` formulas and multi-page PDFs with two-pass `NumberedCanvas` footers; and a Crystal equivalent implementing a 7-band layout system with exact point coordinates for tear-off remittance slips and GAAP operations statements.
- **Result**: Eliminated 100% of proprietary report server licensing fees. Batch execution generated all 17 publication-grade artifacts in under 9 seconds, validated by 67 automated pytest tests.

### Story 3: Performance Optimization on Half-Million Record Relational Ledgers
- **Situation**: As transactional history accumulated to over 500,000 records, critical operational queries like the Delinquency Aging Report and Tenant Payment History began triggering sequential scans and high-memory Sort nodes.
- **Task**: Optimize query execution times and logical I/O without increasing write overhead on OLTP inserts.
- **Action**: Rather than adding generic single-column indexes, I profiled each slow query using `EXPLAIN (ANALYZE, BUFFERS)`. I implemented partial covering indexes for sparse states (e.g. indexing only active overdue charges) and composite B-Trees matching window function `PARTITION BY ... ORDER BY` clauses to eliminate Sort nodes completely.
- **Result**: Reduced shared buffer reads by up to 89.4% on payment histories and 80.0% on rent collection queries. Over 91,200 buffer page reads were saved per query cycle, while partial indexes kept index maintenance overhead on write operations under 10%.
