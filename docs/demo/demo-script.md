# PropLedger — 26-Step End-to-End Demonstrable Demo Script (PL-143)

- **Platform**: PropLedger Enterprise Property Management & Real Estate Analytics
- **Audience**: Technical Interviewers, System Architects, VP of Engineering, Lead Reviewers
- **Execution Engine**: `demo_runner.py` (Automated CLI & Step-by-Step Interactive)
- **Target Database**: PostgreSQL 16 (Docker `propledger-db` on port 5432, 526,846+ records)
- **Backend API**: FastAPI on Python 3.14 (`/api/v1/`)
- **Reporting Engine**: Dual-Engine (SSRS-equivalent Tabular + Crystal-equivalent Section-Banded)

---

## 1. Quick Reference Matrix (All 26 Demo Steps)

| Step # | Domain / Feature Area | Target Component / Stored Procedure | Primary API / CLI Action | Key Verification Criteria |
|:---:|---|---|---|---|
| **01** | Database & Infrastructure | PostgreSQL 16 Container, 36 Tables | `psycopg2` Connection Probe | 36 relational tables verified in `propledger` database |
| **02** | System Diagnostics & Health | Diagnostics Service | `GET /api/v1/diagnostics/health` | HTTP 200, DB `HEALTHY`, reporting engine `ONLINE` |
| **03** | Auth & Identity (Admin) | JWT OAuth2 Authenticator | `POST /api/v1/auth/login` | Bearer token returned with 120-minute expiry |
| **04** | Identity & Security Context | Auth Service (`/auth/me`) | `GET /api/v1/auth/me` | Current user identified as `admin@propledger.com` (`ADMIN`) |
| **05** | Role-Based Access Control | RBAC Middleware | `GET /api/v1/finance/expenses` as non-admin | HTTP 403 Forbidden with RFC 7807 problem details |
| **06** | Asset Hierarchy & Portfolios | Recursive CTE (`vw_AssetHierarchy`) | `GET /api/v1/reports/hierarchy?max_level=4` | 4-level deep tree: Company -> Property -> Building -> Unit |
| **07** | Property Inventory & Metadata | Property Repository | `GET /api/v1/properties/` | 500 enterprise properties enumerated with geo metadata |
| **08** | Unit Inventory & Class Breakdown | Unit Aggregation View | `GET /api/v1/properties/1/units` | Unit count, floor plans, market rent vs square footage |
| **09** | Occupancy Analytics & Rates | `vw_PropertyOccupancy` | `GET /api/v1/properties/occupancy` | Real-time physical occupancy % and vacant unit counts |
| **10** | Tenant Onboarding & Profiles | Tenant Repository | `GET /api/v1/tenants/` | Verified tenant records with contact, status, KYC |
| **11** | Lease Lifecycle Drafting | Lease State Machine | `GET /api/v1/leases/` | Transition from initial draft to validated `ACTIVE` lease |
| **12** | Batch Rent Assessment Engine | `usp_GenerateMonthlyRentCharges` | `POST /api/v1/leases/generate-rent` | Multi-tenant billing charges created with status `PENDING` |
| **13** | Rent Charge Due Date Rules | Check Constraint `chk_rc_due_date` | SQL Constraint Verification | Due date >= charge date enforced; balance intact |
| **14** | Payment Processing (FIFO Alloc) | `usp_RecordPayment` | `POST /api/v1/payments/` | Oldest unpaid charge cleared first via FIFO allocation |
| **15** | Payment Audit Trail & Triggers | `trg_PaymentAuditInsert` | Direct Query on `payment_audit` | Immutable audit log automatically populated by DB trigger |
| **16** | Running Balance & Double-Entry | Window Function `SUM() OVER()` | `GET /api/v1/payments/tenant/1/history` | Rolling cumulative debit/credit balance derived on the fly |
| **17** | Partial Payment & Balance Trace | `usp_RecordPayment` | `POST /api/v1/payments/` (Partial) | Charge status becomes `PARTIALLY_PAID`; remainder tracks |
| **18** | Late Fee Assessment Policy | `finance_rules.py` Late Fee Engine | Evaluation against Policy BR-05 | 5-day grace period honored; flat/daily fee applied |
| **19** | Delinquency Aging Classification | Delinquency Service | `GET /api/v1/collections/delinquent` | Unpaid charges bucketed: 1-30d, 31-60d, 61-90d, 90+d |
| **20** | Collection Escalation Workflow | `usp_EscalateToCollection` | Direct SP invocation on 90+d debt | Auto-generates `collection_cases` record; sets `OVERDUE` |
| **21** | Maintenance Work Order Flow | Maintenance Service | `GET /api/v1/maintenance/` | Tickets grouped by urgency (`HIGH`, `EMERGENCY`) and status |
| **22** | Work Order Audit & Reopen | `usp_ReopenMaintenanceRequest` | `POST /api/v1/maintenance/{id}/reopen` | Closed ticket transitions to `REOPENED` with audit trail |
| **23** | Executive KPI Dashboard View | `vw_DashboardKpis` | `GET /api/v1/reports/occupancy` | High-level portfolio metrics: Occupancy, GPR, Collections |
| **24** | SSRS Publication Engine (Excel) | Report `PL-095` (OpenPyXL) | `GET /api/v1/reports/PL-095/export/excel` | Publication-grade `.xlsx` with frozen panes & `=SUM()` |
| **25** | SSRS Publication Engine (PDF) | Report `PL-096` (ReportLab) | `GET /api/v1/reports/PL-096/export/pdf` | Paginated PDF with `NumberedCanvas` & dynamic headers |
| **26** | Crystal Section-Banded Engine | Statements `CR-01`, `CR-02`, `CR-03` | `GET /api/v1/reports/statements/CR-02/pdf` | Tear-off remittance advice, formal GAAP operations statement |

---

## 2. Interactive Execution Guide

To execute the automated demo suite:
```powershell
# Automated non-stop run
python demo_runner.py --auto

# Interactive step-by-step interview presentation
python demo_runner.py --interactive
```

---

## 3. Detailed Step-by-Step Technical Narratives

### Step 01: Database & Infrastructure Verification
- **Persona**: Lead Database Administrator / DevOps Architect
- **Action**: Probe PostgreSQL 16 on port 5432 and inspect table catalog.
- **Verification**: Query `information_schema.tables` where `table_schema = 'public'`. Exactly 36 tables must be confirmed.
- **Talking Point**: *"PropLedger's relational schema is normalized up to 3NF, supporting comprehensive institutional real estate operations, double-entry payment allocation, audit trails, and strict check constraints."*

### Step 02: System Diagnostics & Health Check
- **Persona**: Platform Reliability Engineer
- **Action**: Query `GET /api/v1/diagnostics/health`.
- **Verification**: Status is `HEALTHY`, database connection pool is active, and reporting engine catalogs (14 SSRS reports, 3 Crystal statements) are loaded.
- **Talking Point**: *"The diagnostics endpoint gives operations teams instantaneous visibility into DB connection pool saturation and reporting service discovery."*

### Step 03: Authentication & JWT Issuance
- **Persona**: Security Architect
- **Action**: Post credentials to `POST /api/v1/auth/login`.
- **Verification**: Receive HMAC-SHA256 bearer token with standard claims (`sub`, `roles`, `exp`).
- **Talking Point**: *"PropLedger enforces stateless, cryptographically signed JWT tokens with bcrypt password hashing."*

### Step 04: Current User Context & Role Verification
- **Persona**: Application Developer
- **Action**: Call `GET /api/v1/auth/me` with Bearer token.
- **Verification**: Identity correctly returns `admin@propledger.com` with role `ADMIN`.
- **Talking Point**: *"Identity context is injected into request lifecycles using FastAPI dependency injection, decoupling authentication from business logic."*

### Step 05: Role-Based Access Control (RBAC) Enforcement
- **Persona**: Security Officer
- **Action**: Issue unauthenticated request or forbidden role request to financial endpoints (`/api/v1/finance/expenses`).
- **Verification**: API returns HTTP 403 Forbidden with RFC 7807 Problem Details payload.
- **Talking Point**: *"Security boundaries are defended at the endpoint level via role guards (`require_roles('ADMIN', 'ACCOUNTANT')`), strictly preventing unauthorized data leakage."*

### Step 06: Multi-Tier Asset Hierarchy Navigation
- **Persona**: Portfolio Asset Manager
- **Action**: Execute recursive CTE hierarchy query (`GET /api/v1/reports/hierarchy?max_level=4`).
- **Verification**: Tree response traverses Company -> Property -> Building -> Unit hierarchy in single SQL query.
- **Talking Point**: *"Instead of issuing recursive N+1 queries, we use a single recursive Common Table Expression (`WITH RECURSIVE`) to traverse property trees in sub-millisecond execution time."*

### Step 07: Enterprise Property Inventory Inspection
- **Persona**: Regional Property Director
- **Action**: Query property inventory (`GET /api/v1/properties/?limit=10`).
- **Verification**: Array of properties returned with gross square footage, year built, and property classifications.
- **Talking Point**: *"The platform models 500 diverse commercial and residential assets across tier-1 metropolitan markets with realistic occupancy and financial characteristics."*

### Step 08: Unit Inventory & Class Breakdown
- **Persona**: Leasing Director
- **Action**: Query unit inventory for Property 1 (`GET /api/v1/properties/1/units`).
- **Verification**: Units categorized by type (`STUDIO`, `1BHK`, `2BHK`, `3BHK`, `RETAIL_SHOP`) with square footage and market rents.
- **Talking Point**: *"Units serve as the atomic revenue-generating nodes in PropLedger, mapping directly to physical spaces and active lease contracts."*

### Step 09: Physical Occupancy Rate Calculations
- **Persona**: Asset Valuation Analyst
- **Action**: Fetch occupancy statistics (`GET /api/v1/properties/occupancy`).
- **Verification**: Pre-aggregated metrics returned (`total_units`, `occupied_units`, `occupancy_percentage`).
- **Talking Point**: *"Zero-math frontend architecture: the user interface never calculates metrics locally; occupancy rates are derived directly by database aggregation views (`vw_PropertyOccupancy`)."*

### Step 10: Tenant Roster & Contact Directory
- **Persona**: Property Manager
- **Action**: Query tenant roster (`GET /api/v1/tenants/?limit=10`).
- **Verification**: Verified tenant records including contact details, active status, and KYC documentation.
- **Talking Point**: *"Tenant profiles maintain complete historical linkage to multiple successive leases, payment methods, and communication logs."*

### Step 11: Lease Agreement Inception & Lifecycle
- **Persona**: Contract Administrator
- **Action**: Inspect active lease agreements (`GET /api/v1/leases/?limit=5`).
- **Verification**: Validated lease contracts with contract rent, security deposit held, and active term dates.
- **Talking Point**: *"Lease state transitions follow an authoritative finite-state machine (`DRAFT` -> `ACTIVE` -> `EXPIRING` -> `RENEWED` / `TERMINATED`). Invalid transitions are blocked at both database and domain layers."*

### Step 12: Automated Monthly Rent Assessment
- **Persona**: Accounts Receivable Manager
- **Action**: Trigger monthly rent charge assessment (`POST /api/v1/leases/generate-rent`).
- **Verification**: Batch generation executes `usp_GenerateMonthlyRentCharges`, producing pending charges across all active leases.
- **Talking Point**: *"Batch rent generation runs atomically within a stored procedure, calculating prorations, recurring fees, and creating unbilled ledger entries."*

### Step 13: Rent Charge Due Date Constraint Verification
- **Persona**: Database Integrity Auditor
- **Action**: Verify check constraint `chk_rc_due_date` across all records.
- **Verification**: Confirm `SELECT COUNT(*) FROM rent_charges WHERE due_date < charge_date` equals 0.
- **Talking Point**: *"Financial data integrity is defended by relational check constraints so that flawed application code can never corrupt the ledger."*

### Step 14: Payment Processing with FIFO Allocation
- **Persona**: AR Specialist
- **Action**: Post payment and trace allocation against oldest outstanding rent charges.
- **Verification**: Payment records created; `payment_allocations` links payment to oldest charges first.
- **Talking Point**: *"Our stored procedure `usp_RecordPayment` utilizes cursor-based FIFO waterfall allocation with row-level locking (`SELECT ... FOR UPDATE`), eliminating concurrency race conditions."*

### Step 15: Payment Audit Trail Verification
- **Persona**: Internal Compliance Auditor
- **Action**: Query `payment_audit` table following payment transactions.
- **Verification**: Immutable trigger-generated record verified with timestamp, action `INSERT`, and amount.
- **Talking Point**: *"Compliance with SOX and statutory financial standards is ensured through database-level triggers (`trg_PaymentAuditInsert`) that write to append-only audit tables."*

### Step 16: Running Balance & Double-Entry Ledger Derivation
- **Persona**: Senior Forensic Accountant
- **Action**: Call `GET /api/v1/payments/tenant/1/history`.
- **Verification**: Rolling running balance correctly tracks cumulative debits and credits: `SUM(debit - credit) OVER (ORDER BY trans_date)`.
- **Talking Point**: *"Running balance is never stored as a mutable column to prevent desynchronization; instead, it is computed on the fly using window functions optimized with composite B-Tree indexes."*

### Step 17: Partial Payment & Overdue Balance Tracking
- **Persona**: AR Analyst
- **Action**: Record partial payment and verify residual status.
- **Verification**: Partially paid charges correctly labeled `PARTIALLY_PAID`, with remaining balance accurately tracked.
- **Talking Point**: *"PropLedger handles complex split allocations across multiple line items without rounding drift or orphan balances."*

### Step 18: Late Fee Assessment & Grace Period Rules
- **Persona**: Collections Manager
- **Action**: Evaluate delinquent accounts against Late Fee Policy BR-05.
- **Verification**: 5-day grace period honored; flat / percentage / daily capped fees accurately calculated.
- **Talking Point**: *"Policy BR-05 is codified into deterministic domain rules with 100% unit test coverage across edge cases (leap years, month-end rollovers, maximum penalty caps)."*

### Step 19: Delinquency Aging Classification
- **Persona**: Credit Risk Officer
- **Action**: Fetch delinquency report (`GET /api/v1/collections/delinquent`).
- **Verification**: Unpaid amounts partitioned into standard 30-day buckets: Current (1-30d), 31-60d, 61-90d, Over 90d.
- **Talking Point**: *"AR aging uses calendar day differentials with index-assisted filtering to immediately isolate high-risk institutional exposure."*

### Step 20: Automated Collection Escalation Workflow
- **Persona**: Legal Counsel / Recovery Specialist
- **Action**: Trigger `usp_EscalateToCollection` on 90+ day delinquent balance.
- **Verification**: Automatic creation of `collection_cases` record; charge statuses updated to `COLLECTION`.
- **Talking Point**: *"Escalation locks the lease from informal renewals and dispatches legal notices, preventing revenue leakage on defaulted assets."*

### Step 21: Maintenance Work Order Management
- **Persona**: Facilities Operations Manager
- **Action**: Query maintenance backlog (`GET /api/v1/maintenance/?limit=10`).
- **Verification**: Work orders retrieved with priority rankings, assigned technicians, and status tracking.
- **Talking Point**: *"Maintenance operations are tightly coupled with unit turnover schedules and vendor dispatch SLAs to maintain asset valuation."*

### Step 22: Work Order Reopening & Audit Trail
- **Persona**: Operations Supervisor
- **Action**: Reopen a closed maintenance ticket (`POST /api/v1/maintenance/1/reopen`).
- **Verification**: Stored procedure `usp_ReopenMaintenanceRequest` transitions ticket to `REOPENED` and appends audit note.
- **Talking Point**: *"Work order state transitions maintain strict audit trails so chronic mechanical failures can be flagged for capital replacement."*

### Step 23: Executive Portfolio Analytics Dashboard
- **Persona**: Chief Executive Officer / Institutional Investor
- **Action**: Query portfolio aggregate analytics.
- **Verification**: C-level portfolio summary: overall occupancy rate, gross potential revenue, collections efficiency.
- **Talking Point**: *"Real-time C-suite visibility across 500+ properties, powered by materialized and indexed analytical views without OLTP locking."*

### Step 24: SSRS Publication Engine — Excel Export with Formulas (PL-095)
- **Persona**: Financial Controller
- **Action**: Export Rent Roll Summary (`GET /api/v1/reports/PL-095/export/excel`).
- **Verification**: OpenPyXL `.xlsx` binary workbook containing navy headers, zebra striping, and live `=SUM()` formula rows.
- **Talking Point**: *"Unlike naive CSV exports, our reporting engine generates fully formatted OpenPyXL spreadsheets containing live `=SUM()` formulas so analysts can audit totals directly in Excel."*

### Step 25: SSRS Publication Engine — NumberedCanvas Paginated PDF (PL-096)
- **Persona**: Compliance Reporting Auditor
- **Action**: Export Tenant Aging Report (`GET /api/v1/reports/PL-096/export/pdf`).
- **Verification**: ReportLab PDF stream starting with `%PDF-1.4`, dynamic header block, and two-pass `Page X of Y` footers.
- **Talking Point**: *"By leveraging a custom ReportLab `NumberedCanvas`, we solve the classic PDF multi-page problem, calculating total page count on a second pass for publication-grade output."*

### Step 26: Crystal Reports Section-Banded Engine (CR-01, CR-02, CR-03)
- **Persona**: Certified Public Accountant / Fund Auditor
- **Action**: Export formal statements (`GET /api/v1/reports/statements/CR-02/pdf`).
- **Verification**: Formal columnar rent roll rendered with section-banded architecture and economic occupancy audit reconciliations.
- **Talking Point**: *"This Section-Banded report engine replicates SAP Crystal Reports' exact 7-band layout (Report Header, Page Header, Group Header, Details, Group Footer, Page Footer, Report Summary), allowing legacy enterprise systems to modernize to Python without losing visual fidelity."*

---
