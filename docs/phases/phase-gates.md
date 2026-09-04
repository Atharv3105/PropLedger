# PropLedger — Phase Gates & Exit Criteria
## Strict Phase-Gated Progression Controls (PRD Part A3 & A4)

---

## Gate Protocol & Execution Rules

1. **Sequential Progression**: Phases must be executed in exact numeric order (Phase 0 through Phase 10). Jumping ahead is prohibited.
2. **Binary Gate Criteria**: Every gate condition is evaluated as strictly **PASS** or **FAIL**. There is no partial pass.
3. **Artifact Verification**: Prior phase outputs must be directly consumed by the succeeding phase (e.g. Phase 4 API strictly consumes Phase 2 SQL procedures).
4. **Phase Completion Report**: Each phase concludes with an official `/docs/phases/phase-XX-completion.md` report before the next phase commences.

---

## Phase Gate Checklists

### PHASE 0 — Requirements & Execution Control
- [x] Full PRD parsed; all statements translated to unique IDs (`PL-001` through `PL-145`).
- [x] Traceability matrix created with all required columns (`requirements-traceability.md`).
- [x] Technology stack substitutions documented and user-approved.
- [x] Host environment audited and documented (`dependency-checklist.md`).
- [x] Repository folder skeleton matches PRD Parts AG & AH with `.gitkeep` files.
- [x] Git repository initialized with clean `.gitignore`.
- [x] Architecture overview, reporting pipeline, and baseline database design documented.
- [x] Phase 0 Completion Report created with Gate Status: **PASS**.

### PHASE 1 — Database Foundation
- [ ] PostgreSQL 16 container / database deployed and accessible.
- [ ] DDL scripts execute cleanly without errors (`01_schema/`, `02_tables/`, `03_constraints/`).
- [ ] All ~25 entities, primary keys, foreign keys, and CHECK constraints deployed.
- [ ] Standard audit columns (`created_by`, `created_at`, `modified_by`, `modified_at`) present.
- [ ] Dedicated history tables deployed (`lease_history`, `payment_audit`, `status_history`).
- [ ] Seed data scripts generate 500+ properties, units, tenants, and initial leases.
- [ ] Database tests pass: Referential integrity, check constraints, unique constraints.
- [ ] Phase 1 Completion Report created with Gate Status: **PASS**.

### PHASE 2 — Advanced SQL
- [ ] Complex JOINs demonstrated: INNER JOIN, LEFT JOIN, SELF JOIN.
- [ ] Subqueries demonstrated: Scalar, Correlated, EXISTS, NOT EXISTS.
- [ ] CTEs demonstrated: Ordinary CTE, Recursive asset/org hierarchy CTE.
- [ ] Window functions demonstrated: `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `SUM OVER`.
- [ ] PIVOT / Cross-tabulation demonstrated for Property x Monthly Rent.
- [ ] Conditional aggregation demonstrated (`SUM(CASE WHEN ...)`).
- [ ] All 7 named views created and returning verified datasets.
- [ ] All 7 named stored procedures created and tested.
- [ ] All 3 named functions created and tested.
- [ ] Selective triggers created for payment audit and lease status change.
- [ ] Phase 2 Completion Report created with Gate Status: **PASS**.

### PHASE 3 — Business Workflows
- [ ] Full lease lifecycle operational (Draft -> Active -> Expiring -> Expired -> Renewed).
- [ ] Monthly rent generation batch operational (`usp_GenerateMonthlyRent`).
- [ ] Transactional payment processing operational with atomic rollback on simulated failure (`usp_RecordPayment`).
- [ ] Partial payment logic verified (reduces balance, does not settle charge, correct FIFO allocation).
- [ ] Late fee calculation verified (respects grace period, calculates flat/percentage fee).
- [ ] Delinquency aging classification verified (Current, 1-30, 31-60, 61-90, 90+ days).
- [ ] Maintenance workflow verified (Work order assignment, resolution, cost recording).
- [ ] Business rule BR-08 verified: Closed maintenance requests block work orders until reopened.
- [ ] Phase 3 Completion Report created with Gate Status: **PASS**.

### PHASE 4 — Backend API (FastAPI)
- [ ] FastAPI application structured cleanly (routers, services, schemas, repositories).
- [ ] JWT authentication and role-based access control (RBAC) enforced server-side.
- [ ] Pydantic schemas validate all incoming payloads; reject negative payments, invalid dates.
- [ ] Database access layer executes SQL stored procedures and parameterized queries safely.
- [ ] Global exception handler returns RFC 7807 problem details; zero raw DB exceptions exposed.
- [ ] Representative endpoints functional (`/api/properties`, `/api/leases`, `/api/payments`, `/api/reports/*`).
- [ ] Automated API integration tests pass.
- [ ] Phase 4 Completion Report created with Gate Status: **PASS**.

### PHASE 5 — Frontend Application (React)
- [ ] React 18 + TypeScript + Vite application builds cleanly without compiler errors.
- [ ] Enterprise navigation matches PRD: Dashboard, Properties, Tenants, Leases, Payments, Collections, Maintenance, Vendors, Finance, Reports, Admin.
- [ ] Role-aware navigation renders views appropriate to logged-in role.
- [ ] Dashboard displays authoritative KPIs: Total Properties, Units, Occupancy %, Revenue, Outstanding, Collection %, Open Maintenance, Expiring Leases.
- [ ] Interactive charts visualize trends using data strictly fetched from the API.
- [ ] TanStack Query manages caching, loading states, and error handling.
- [ ] Phase 5 Completion Report created with Gate Status: **PASS**.

### PHASE 6 — SSRS Reporting Equivalent
- [ ] All 14 required report families implemented and functional.
- [ ] Parameterized execution supported (Property filter, Date range, Status).
- [ ] Grouping, multi-level sorting, and aggregations (subtotals, grand totals) verified.
- [ ] Conditional formatting applied (highlighting overdue accounts, low occupancy).
- [ ] Export pipeline produces styled, paginated PDF documents (WeasyPrint).
- [ ] Export pipeline produces formatted Excel (.xlsx) workbooks (openpyxl).
- [ ] Report catalog documentation complete.
- [ ] Phase 6 Completion Report created with Gate Status: **PASS**.

### PHASE 7 — Crystal Reports Equivalent
- [ ] 3 required Crystal-equivalent reports functional (Tenant Payment History, Rent Roll, Income & Expense).
- [ ] Rendered via ReportLab with formal corporate statement layouts and exact point alignment.
- [ ] Comprehensive documentation detailing reporting differences (SSRS vs Crystal architecture).
- [ ] Phase 7 Completion Report created with Gate Status: **PASS**.

### PHASE 8 — Performance Engineering
- [ ] Synthetic dataset scaled to 100,000+ records to ensure measurable query execution.
- [ ] 5 required performance case studies executed with real metrics (not fabricated).
- [ ] Before and after metrics recorded: Execution Time, CPU Time, Logical Reads, Execution Plans.
- [ ] Indexing strategy applied: Clustered/PK, composite, and covering indexes justified.
- [ ] Performance markdown reports created under `/docs/performance/`.
- [ ] Phase 8 Completion Report created with Gate Status: **PASS**.

### PHASE 9 — Testing & Quality Validation
- [ ] Backend unit tests pass (late fee, balance, lease status, delinquency).
- [ ] Integration tests pass for full critical path (Lease -> Rent -> Partial Payment -> Balance -> Late Fee -> Delinquency -> Collection).
- [ ] SQL test scripts validate constraints, stored procedures, transactions, and rollback.
- [ ] Report validation tests confirm parameter filtering, totals, and export fidelity.
- [ ] Zero critical unhandled errors or untested PRD requirements.
- [ ] Phase 9 Completion Report created with Gate Status: **PASS**.

### PHASE 10 — Interview & Portfolio Packaging
- [ ] Root README complete with architecture, tech stack, and setup guide.
- [ ] Architecture diagram, ER diagram, and reporting workflow documented.
- [ ] Complete 26-step demonstrable end-to-end demo script documented and runnable.
- [ ] Final PRD Audit (`docs/final-prd-audit.md`) passes with 100% requirement traceability.
- [ ] Interview discussion guide prepared covering SQL, performance, and application support.
- [ ] Phase 10 Completion Report created with Gate Status: **PASS**.
