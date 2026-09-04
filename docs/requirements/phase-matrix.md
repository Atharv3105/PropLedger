# PropLedger — Phase-to-Requirement Matrix
## Mapping Requirements (PL-NNN) to Development Phases

This document governs phase execution order and guarantees zero requirement leakage.

### PHASE 0 — Requirements & Execution Control

| ID | Requirement |
|---|---|
| `Core` | Requirements parsing, traceability matrix, phase gates, repo skeleton, dependency audit |

### PHASE 1 — Database Foundation

| ID | Requirement |
|---|---|
| `PL-001` | Administrator Role implementation with full system control |
| `PL-002` | Property Manager Role implementation managing properties, leases, maintenance |
| `PL-003` | Leasing / Front Office Staff Role implementation handling applications and renewals |
| `PL-004` | Accountant / Finance Staff Role implementation handling rent, invoices, expenses |
| `PL-005` | Maintenance Staff Role implementation handling work orders and vendors |
| `PL-006` | Property Owner Role implementation viewing property-level financial reports |
| `PL-007` | Tenant Role implementation viewing leases, obligations, payments, requests |
| `PL-010` | Password Hashing using bcrypt with salt rounds |
| `PL-011` | Create property with name, address, owner assignment, property type |
| `PL-012` | Edit property details and update metadata |
| `PL-013` | Assign property owner with historical tracking |
| `PL-014` | Define Property Types: Residential, Commercial, Mixed |
| `PL-015` | Add and manage buildings within a property |
| `PL-016` | Add and manage units within buildings / properties |
| `PL-017` | Define unit types: Studio, 1BHK, 2BHK, 3BHK, Commercial Office, Retail |
| `PL-018` | Define baseline market rent and target rent per unit |
| `PL-019` | Unit Status state machine: Available, Occupied, Reserved, Maintenance, Inactive |
| `PL-022` | Tenant Personal Information capture (first name, last name, DOB, tax ID) |
| `PL-023` | Tenant Contact Information (email, phone, alternate phone, emergency contacts) |
| `PL-024` | Tenant Identification Reference (National ID / Passport / Driving License) |
| `PL-025` | Tenant Occupancy Details linking active lease, unit, and move-in dates |
| `PL-026` | Preserve historical tenant relationships without overwriting past records |
| `PL-030` | Tenant Maintenance History tracking requests submitted by tenant |
| `PL-031` | Lease core attributes: Unit, Tenant, Start/End Dates, Monthly Rent, Security Deposit |
| `PL-032` | Late Fee Policy configuration per lease (grace period days, fixed/percentage fee) |
| `PL-033` | Rent Due Day definition (e.g. 1st or 5th of every month) |
| `PL-034` | Lease Renewal Status tracking: Pending, Renewed, Non-Renewal |
| `PL-035` | Lease States: Draft, Active, Expiring, Expired, Terminated, Renewed |
| `PL-038` | Multi-tenant lease association supporting primary and co-signers |
| `PL-046` | Tenant balance tracking table and view maintaining running ledger |
| `PL-049` | Collection Case creation and tracking for delinquent tenants |
| `PL-050` | Collection Follow-up activity logging (calls, notices, formal warnings) |
| `PL-053` | Maintenance Request creation with Unit, Tenant, Property, Category, Priority |
| `PL-054` | Maintenance Status lifecycle: Open, Assigned, In Progress, On Hold, Resolved, Closed |
| `PL-055` | Work Order assignment to internal staff or external vendor |
| `PL-060` | Vendor Profile management with contact info and service category |
| `PL-061` | Track vendor assigned work orders and cost disbursements |
| `PL-063` | Property Income tracking: Rent, late fees, utilities, other income |
| `PL-064` | Property Expense tracking: Maintenance, utilities, vendor invoices, admin |
| `PL-066` | Security Deposit tracking: collected deposit, escrow status, deductions, refund |
| `PL-BR-01` | BR-01: An occupied unit must have at least one active lease |
| `PL-BR-02` | BR-02: A lease cannot begin after its end date |
| `PL-089` | Database Auditing: CreatedBy, CreatedAt, ModifiedBy, ModifiedAt columns across entities |
| `PL-090` | Dedicated History Tables: LeaseHistory, PaymentAudit, RentAdjustmentHistory, StatusChangeHistory |
| `PL-091` | Synthetic Data Generation script producing 500-1,000 properties |
| `PL-092` | Synthetic Data: Several thousand units, tenants, and leases |
| `PL-093` | Synthetic Data: Hundreds of thousands of rent and payment records for performance tests |
| `PL-094` | Synthetic Data: Thousands of maintenance requests, work orders, and expenses |
| `PL-137` | Indexing Strategy: Document justification, query benefit, and maintenance trade-offs for all indexes |
| `PL-143` | Complete 26-Step End-to-End Demonstrable Demo Script |
| `PL-144` | Final PRD Compliance Audit verifying every single requirement with proof and evidence |
| `PL-145` | Interview Preparation Package: Architecture narrative, technical priorities, SQL problem-solving case studies |

### PHASE 2 — Advanced SQL

| ID | Requirement |
|---|---|
| `PL-020` | Track property occupancy percentage dynamically from unit statuses |
| `PL-027` | Tenant Lease History view displaying past, current, and renewed leases |
| `PL-028` | Tenant Payment History view displaying all charges, payments, and receipts |
| `PL-029` | Tenant Outstanding Balance dynamic calculation |
| `PL-036` | Automatic identification of upcoming lease expirations (30/60/90 days) |
| `PL-039` | Generate Monthly Rent charges for all active leases |
| `PL-040` | Record Payment against active lease and outstanding rent charges |
| `PL-042` | Late Fee automated calculation after grace period expires |
| `PL-046` | Tenant balance tracking table and view maintaining running ledger |
| `PL-048` | Aging Categories classification: Current, 1-30, 31-60, 61-90, 90+ Days |
| `PL-058` | Calculate Average Resolution Time KPI per property and category |
| `PL-059` | Calculate Maintenance Cost per property and Requests by Category |
| `PL-062` | Evaluate Vendor Performance and average completion turnaround times |
| `PL-063` | Property Income tracking: Rent, late fees, utilities, other income |
| `PL-065` | Calculate Net Operating Result / Profitability per property |
| `PL-BR-05` | BR-05: Late fees apply only after configured grace period expires |
| `PL-BR-06` | BR-06: Delinquency status depends on outstanding amount and overdue duration |
| `PL-067` | Complex Joins: Demonstrate INNER JOIN, LEFT JOIN, and SELF JOIN |
| `PL-068` | Subqueries: Demonstrate Scalar, Correlated, EXISTS, and NOT EXISTS queries |
| `PL-069` | CTEs: Ordinary CTE and Recursive CTE (e.g. organizational or asset hierarchy) |
| `PL-070` | Window Functions: ROW_NUMBER(), RANK(), DENSE_RANK(), LAG(), LEAD(), SUM() OVER() |
| `PL-071` | PIVOT Analysis: Property x Monthly Rent Collection cross-tabulation |
| `PL-072` | Conditional Aggregation: SUM(CASE WHEN ... THEN ... END) for financial aging |
| `PL-073` | Named View: vw_PropertyOccupancy |
| `PL-074` | Named View: vw_TenantOutstandingBalance |
| `PL-075` | Named View: vw_ActiveLeases |
| `PL-076` | Named View: vw_PropertyFinancialSummary |
| `PL-077` | Named Stored Procedure: usp_GenerateMonthlyRent |
| `PL-078` | Named Stored Procedure: usp_RecordPayment |
| `PL-079` | Named Stored Procedure: usp_GetTenantPaymentHistory |
| `PL-080` | Named Stored Procedure: usp_GetPropertyOccupancy |
| `PL-081` | Named Stored Procedure: usp_GetDelinquencyReport |
| `PL-082` | Named Stored Procedure: usp_GetLeaseExpiryReport |
| `PL-083` | Named Stored Procedure: usp_GetPropertyFinancialSummary |
| `PL-084` | Named Function: fn_CalculateLateFee() |
| `PL-085` | Named Function: fn_GetOutstandingBalance() |
| `PL-086` | Named Function: fn_GetLeaseStatus() |
| `PL-087` | Selective Triggers: Payment audit record creation on payment insertion |
| `PL-088` | Selective Triggers: Lease status change history logging |
| `PL-095` | Report 1: Property Occupancy Report (Total, Occupied, Vacant, Maintenance, %) |
| `PL-096` | Report 2: Unit Availability Report (Property, Building, Unit Type, Rent Range) |
| `PL-097` | Report 3: Tenant Directory (Tenant, Unit, Property, Lease, Contact, Status) |
| `PL-098` | Report 4: Lease Expiration Report (From, To, Property, Days Remaining, Renewal Status) |
| `PL-099` | Report 5: Monthly Rent Collection Report (Expected, Collected, Outstanding, Late Fees, %) |
| `PL-100` | Report 6: Delinquency Report (Tenant, Property, Amount Due, Overdue Days, Aging Category) |
| `PL-101` | Report 7: Tenant Payment History (Tenant, Lease, Invoice, Date, Amount, Method, Balance) |
| `PL-102` | Report 8: Security Deposit Report (Tenant, Deposit, Date, Status, Deductions, Refund) |
| `PL-103` | Report 9: Maintenance Performance Report (Property, Requests, Open, Closed, Avg Time, Cost) |
| `PL-104` | Report 10: Property Income & Expense Report (Income, Expenses, Net Operating Result) |
| `PL-105` | Report 11: Monthly Property Summary (Management-oriented combined executive report) |
| `PL-106` | Report 12: Owner / Executive Dashboard Report (Occupancy, Revenue, Collection %, Cost) |
| `PL-107` | Report 13: Rent Roll (Property, Unit, Tenant, Lease, Monthly Rent, Status, Balance) |
| `PL-108` | Report 14: Lease Renewal Report (Expiring leases, Renewed, Pending renewals, Non-renewals) |

### PHASE 3 — Business Workflows

| ID | Requirement |
|---|---|
| `PL-019` | Unit Status state machine: Available, Occupied, Reserved, Maintenance, Inactive |
| `PL-021` | Mark units Available / Occupied / Maintenance with transition validation |
| `PL-025` | Tenant Occupancy Details linking active lease, unit, and move-in dates |
| `PL-026` | Preserve historical tenant relationships without overwriting past records |
| `PL-029` | Tenant Outstanding Balance dynamic calculation |
| `PL-032` | Late Fee Policy configuration per lease (grace period days, fixed/percentage fee) |
| `PL-034` | Lease Renewal Status tracking: Pending, Renewed, Non-Renewal |
| `PL-035` | Lease States: Draft, Active, Expiring, Expired, Terminated, Renewed |
| `PL-037` | Lease Renewal workflow: generate renewed lease term linking predecessor |
| `PL-039` | Generate Monthly Rent charges for all active leases |
| `PL-040` | Record Payment against active lease and outstanding rent charges |
| `PL-041` | Partial Payment processing reducing balance without settling full charge |
| `PL-042` | Late Fee automated calculation after grace period expires |
| `PL-043` | Payment Allocation logic: apply payments to oldest charges first (FIFO) |
| `PL-044` | Transactional Payment Processing with atomic rollback on failure |
| `PL-045` | Payment validation: disallow negative amount, payment on invalid/terminated lease |
| `PL-047` | Delinquency status identification based on overdue days and threshold |
| `PL-048` | Aging Categories classification: Current, 1-30, 31-60, 61-90, 90+ Days |
| `PL-051` | Collection Settlement recording with agreed payout terms |
| `PL-052` | Delinquent debt Write-off recording with reason and manager signoff |
| `PL-054` | Maintenance Status lifecycle: Open, Assigned, In Progress, On Hold, Resolved, Closed |
| `PL-056` | Maintenance Resolution recording with completion date, notes, and actual cost |
| `PL-057` | Rule BR-08 enforcement: closed maintenance request cannot receive work without reopening |
| `PL-066` | Security Deposit tracking: collected deposit, escrow status, deductions, refund |
| `PL-BR-01` | BR-01: An occupied unit must have at least one active lease |
| `PL-BR-03` | BR-03: A payment cannot be recorded against an invalid or inactive lease |
| `PL-BR-04` | BR-04: Partial payment reduces balance but does not fully settle rent charge |
| `PL-BR-05` | BR-05: Late fees apply only after configured grace period expires |
| `PL-BR-06` | BR-06: Delinquency status depends on outstanding amount and overdue duration |
| `PL-BR-07` | BR-07: A terminated lease cannot generate new rent charges |
| `PL-BR-08` | BR-08: A closed maintenance request cannot receive further work without reopening |
| `PL-BR-10` | BR-10: Payment processing must be atomic with full rollback on error |
| `PL-078` | Named Stored Procedure: usp_RecordPayment |
| `PL-087` | Selective Triggers: Payment audit record creation on payment insertion |
| `PL-088` | Selective Triggers: Lease status change history logging |

### PHASE 4 — Backend API (FastAPI)

| ID | Requirement |
|---|---|
| `PL-001` | Administrator Role implementation with full system control |
| `PL-002` | Property Manager Role implementation managing properties, leases, maintenance |
| `PL-003` | Leasing / Front Office Staff Role implementation handling applications and renewals |
| `PL-004` | Accountant / Finance Staff Role implementation handling rent, invoices, expenses |
| `PL-005` | Maintenance Staff Role implementation handling work orders and vendors |
| `PL-006` | Property Owner Role implementation viewing property-level financial reports |
| `PL-007` | Tenant Role implementation viewing leases, obligations, payments, requests |
| `PL-008` | Server-Side RBAC Enforcement preventing client-side permission bypass |
| `PL-009` | Secure Authentication via JWT tokens with refresh/expiration mechanism |
| `PL-010` | Password Hashing using bcrypt with salt rounds |
| `PL-011` | Create property with name, address, owner assignment, property type |
| `PL-012` | Edit property details and update metadata |
| `PL-013` | Assign property owner with historical tracking |
| `PL-015` | Add and manage buildings within a property |
| `PL-016` | Add and manage units within buildings / properties |
| `PL-018` | Define baseline market rent and target rent per unit |
| `PL-020` | Track property occupancy percentage dynamically from unit statuses |
| `PL-021` | Mark units Available / Occupied / Maintenance with transition validation |
| `PL-022` | Tenant Personal Information capture (first name, last name, DOB, tax ID) |
| `PL-023` | Tenant Contact Information (email, phone, alternate phone, emergency contacts) |
| `PL-024` | Tenant Identification Reference (National ID / Passport / Driving License) |
| `PL-027` | Tenant Lease History view displaying past, current, and renewed leases |
| `PL-028` | Tenant Payment History view displaying all charges, payments, and receipts |
| `PL-029` | Tenant Outstanding Balance dynamic calculation |
| `PL-030` | Tenant Maintenance History tracking requests submitted by tenant |
| `PL-031` | Lease core attributes: Unit, Tenant, Start/End Dates, Monthly Rent, Security Deposit |
| `PL-036` | Automatic identification of upcoming lease expirations (30/60/90 days) |
| `PL-037` | Lease Renewal workflow: generate renewed lease term linking predecessor |
| `PL-040` | Record Payment against active lease and outstanding rent charges |
| `PL-041` | Partial Payment processing reducing balance without settling full charge |
| `PL-045` | Payment validation: disallow negative amount, payment on invalid/terminated lease |
| `PL-047` | Delinquency status identification based on overdue days and threshold |
| `PL-049` | Collection Case creation and tracking for delinquent tenants |
| `PL-050` | Collection Follow-up activity logging (calls, notices, formal warnings) |
| `PL-051` | Collection Settlement recording with agreed payout terms |
| `PL-052` | Delinquent debt Write-off recording with reason and manager signoff |
| `PL-053` | Maintenance Request creation with Unit, Tenant, Property, Category, Priority |
| `PL-055` | Work Order assignment to internal staff or external vendor |
| `PL-056` | Maintenance Resolution recording with completion date, notes, and actual cost |
| `PL-057` | Rule BR-08 enforcement: closed maintenance request cannot receive work without reopening |
| `PL-058` | Calculate Average Resolution Time KPI per property and category |
| `PL-059` | Calculate Maintenance Cost per property and Requests by Category |
| `PL-060` | Vendor Profile management with contact info and service category |
| `PL-061` | Track vendor assigned work orders and cost disbursements |
| `PL-062` | Evaluate Vendor Performance and average completion turnaround times |
| `PL-064` | Property Expense tracking: Maintenance, utilities, vendor invoices, admin |
| `PL-065` | Calculate Net Operating Result / Profitability per property |
| `PL-066` | Security Deposit tracking: collected deposit, escrow status, deductions, refund |
| `PL-BR-09` | BR-09: Only authorized roles can access financial data |
| `PL-122` | Authoritative KPI source of truth enforcement: frontend strictly consumes API/DB calculations without re-computing |
| `PL-124` | FastAPI modular application architecture with routers, services, schemas, repositories |
| `PL-125` | Database connection pooling and async query execution via SQLAlchemy and asyncpg |
| `PL-126` | Global exception handling middleware translating DB constraints to clean RFC 7807 problem details |
| `PL-127` | Structured JSON logging with request ID tracking and execution time diagnostics |
| `PL-128` | System Diagnostics endpoint and view: DB Connectivity, Report Service, Last Report, Slow Queries, Errors |
| `PL-129` | Application Support Troubleshooting Log: Incident, Root Cause, Resolution, Preventive Action |
| `PL-130` | Client Report Builder: User selects Property, Date Range, Metrics, Grouping, Format to generate custom report |

### PHASE 5 — Frontend Application (React)

| ID | Requirement |
|---|---|
| `PL-011` | Create property with name, address, owner assignment, property type |
| `PL-012` | Edit property details and update metadata |
| `PL-015` | Add and manage buildings within a property |
| `PL-016` | Add and manage units within buildings / properties |
| `PL-022` | Tenant Personal Information capture (first name, last name, DOB, tax ID) |
| `PL-023` | Tenant Contact Information (email, phone, alternate phone, emergency contacts) |
| `PL-027` | Tenant Lease History view displaying past, current, and renewed leases |
| `PL-028` | Tenant Payment History view displaying all charges, payments, and receipts |
| `PL-030` | Tenant Maintenance History tracking requests submitted by tenant |
| `PL-031` | Lease core attributes: Unit, Tenant, Start/End Dates, Monthly Rent, Security Deposit |
| `PL-049` | Collection Case creation and tracking for delinquent tenants |
| `PL-050` | Collection Follow-up activity logging (calls, notices, formal warnings) |
| `PL-053` | Maintenance Request creation with Unit, Tenant, Property, Category, Priority |
| `PL-055` | Work Order assignment to internal staff or external vendor |
| `PL-060` | Vendor Profile management with contact info and service category |
| `PL-118` | React 18 + TypeScript + Vite project bootstrap with clean directory architecture |
| `PL-119` | Main Navigation: Dashboard, Properties, Tenants, Leases, Payments, Collections, Maintenance, Vendors, Finance, Reports, Admin |
| `PL-120` | Dashboard KPIs: Total Properties, Total Units, Occupancy %, Revenue, Outstanding, Collection %, Open Maintenance, Expiring Leases |
| `PL-121` | Dashboard Visualizations: Occupancy Trend, Revenue Trend, Collection %, Delinquency Aging, Maintenance Breakdown |
| `PL-122` | Authoritative KPI source of truth enforcement: frontend strictly consumes API/DB calculations without re-computing |
| `PL-123` | TanStack Query state management with caching, query invalidation on mutation, error states |
| `PL-128` | System Diagnostics endpoint and view: DB Connectivity, Report Service, Last Report, Slow Queries, Errors |
| `PL-130` | Client Report Builder: User selects Property, Date Range, Metrics, Grouping, Format to generate custom report |

### PHASE 6 — SSRS Reporting Equivalent

| ID | Requirement |
|---|---|
| `PL-095` | Report 1: Property Occupancy Report (Total, Occupied, Vacant, Maintenance, %) |
| `PL-096` | Report 2: Unit Availability Report (Property, Building, Unit Type, Rent Range) |
| `PL-097` | Report 3: Tenant Directory (Tenant, Unit, Property, Lease, Contact, Status) |
| `PL-098` | Report 4: Lease Expiration Report (From, To, Property, Days Remaining, Renewal Status) |
| `PL-099` | Report 5: Monthly Rent Collection Report (Expected, Collected, Outstanding, Late Fees, %) |
| `PL-100` | Report 6: Delinquency Report (Tenant, Property, Amount Due, Overdue Days, Aging Category) |
| `PL-101` | Report 7: Tenant Payment History (Tenant, Lease, Invoice, Date, Amount, Method, Balance) |
| `PL-102` | Report 8: Security Deposit Report (Tenant, Deposit, Date, Status, Deductions, Refund) |
| `PL-103` | Report 9: Maintenance Performance Report (Property, Requests, Open, Closed, Avg Time, Cost) |
| `PL-104` | Report 10: Property Income & Expense Report (Income, Expenses, Net Operating Result) |
| `PL-105` | Report 11: Monthly Property Summary (Management-oriented combined executive report) |
| `PL-106` | Report 12: Owner / Executive Dashboard Report (Occupancy, Revenue, Collection %, Cost) |
| `PL-107` | Report 13: Rent Roll (Property, Unit, Tenant, Lease, Monthly Rent, Status, Balance) |
| `PL-108` | Report 14: Lease Renewal Report (Expiring leases, Renewed, Pending renewals, Non-renewals) |
| `PL-109` | Reporting Engine: Parameterized execution (Date range, Property filter, Status filter) |
| `PL-110` | Reporting Engine: Grouping, Multi-level sorting, and Aggregations (Subtotals, Grand Totals) |
| `PL-111` | Reporting Engine: Conditional formatting (Highlighting delinquent rows, low occupancy) |
| `PL-112` | Reporting Engine: Export pipeline generating professional PDF with headers/footers/page numbers |
| `PL-113` | Reporting Engine: Export pipeline generating formatted Excel (.xlsx) workbooks |
| `PL-131` | Client Requirement Case Study: Full lifecycle documentation (Requirement -> Analysis -> Query -> SP -> Report -> Test -> Deploy) |

### PHASE 7 — Crystal Reports Equivalent

| ID | Requirement |
|---|---|
| `PL-114` | Crystal Equivalent Report 1: Tenant Payment History statement layout |
| `PL-115` | Crystal Equivalent Report 2: Property Rent Roll formal columnar layout |
| `PL-116` | Crystal Equivalent Report 3: Property Income & Expense formal financial statement |
| `PL-117` | Multi-Reporting Engine comparative documentation (Architecture, data flow, SSRS vs Crystal) |

### PHASE 8 — Performance Engineering

| ID | Requirement |
|---|---|
| `PL-132` | Performance Case Study 1: Slow Property Occupancy query optimization with before/after execution plans |
| `PL-133` | Performance Case Study 2: Large Payment History query optimization with before/after execution plans |
| `PL-134` | Performance Case Study 3: Monthly Collection Aggregation query optimization |
| `PL-135` | Performance Case Study 4: Delinquency Aging Report optimization under heavy volume |
| `PL-136` | Performance Case Study 5: Property Financial Summary aggregation optimization |
| `PL-137` | Indexing Strategy: Document justification, query benefit, and maintenance trade-offs for all indexes |
| `PL-142` | Performance Benchmark Tests: Execution time, memory, logical reads against synthetic dataset |

### PHASE 9 — Testing & Quality Validation

| ID | Requirement |
|---|---|
| `PL-138` | Automated Unit Tests: Late-fee calculation, balance derivation, lease status, delinquency classification |
| `PL-139` | Automated Integration Tests: Full critical financial lifecycle (Lease -> Rent -> Partial Payment -> Balance -> Late Fee -> Delinquency -> Collection) |
| `PL-140` | Automated Database Tests: Constraints, stored procedures, transactions, triggers, referential integrity |
| `PL-141` | Automated Report Validation Tests: Parameter filtering, totals/aggregations, date ranges, null handling, export outputs |
| `PL-142` | Performance Benchmark Tests: Execution time, memory, logical reads against synthetic dataset |

### PHASE 10 — Interview & Portfolio Packaging

| ID | Requirement |
|---|---|
| `PL-143` | Complete 26-Step End-to-End Demonstrable Demo Script |
| `PL-144` | Final PRD Compliance Audit verifying every single requirement with proof and evidence |
| `PL-145` | Interview Preparation Package: Architecture narrative, technical priorities, SQL problem-solving case studies |
