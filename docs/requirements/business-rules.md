# PropLedger — Business Rules Register
## Part W Business Rules Specification & Enforcement Strategy

Every business rule specified in PRD Part W is defined below with its strict enforcement tier, validation logic, and test coverage.

### BR-01 — An occupied unit must have at least one active lease.
- **Enforcement Tier**: Database Check / Trigger + API Validation Service
- **Validation Logic**: When a unit's status is updated to 'Occupied', a check ensures `EXISTS (SELECT 1 FROM leases WHERE unit_id = :id AND status = 'ACTIVE')`. Conversely, if the last active lease terminates, unit status automatically transitions to 'Available' or 'Turnover'.
- **Business Justification**: Prevent vacant units being marked occupied without legal contract.
- **Test Coverage**: `test_br01_occupied_unit.py`, DB trigger test `08_triggers/trg_CheckUnitLeaseStatus.sql`
- **Status**: `DEFINED` (Phase 0 Baseline)

### BR-02 — A lease cannot begin after its end date.
- **Enforcement Tier**: Database Table Constraint (`CHECK (start_date <= end_date)`) + Pydantic Schema Validator
- **Validation Logic**: Enforced at DDL level. Attempting to insert or update a lease where `start_date > end_date` throws a DB check constraint violation (SQLSTATE 23514). API returns HTTP 422 Unprocessable Entity.
- **Business Justification**: Prevent temporal inconsistencies and negative duration calculations in rent roll.
- **Test Coverage**: `test_br02_lease_dates.py`, DDL constraint test
- **Status**: `DEFINED` (Phase 0 Baseline)

### BR-03 — A payment cannot be recorded against an invalid or inactive lease.
- **Enforcement Tier**: Stored Procedure (`usp_RecordPayment`) + API PaymentService
- **Validation Logic**: Before inserting into `payments`, the procedure verifies that the `lease_id` exists and has `status IN ('ACTIVE', 'EXPIRING', 'DELINQUENT')`. Payments on 'DRAFT' or 'TERMINATED' leases are rejected with custom exception.
- **Business Justification**: Prevent rogue financial entries against non-existent or terminated contracts.
- **Test Coverage**: `test_br03_payment_lease.py`, SP unit test
- **Status**: `DEFINED` (Phase 0 Baseline)

### BR-04 — A partial payment reduces outstanding balance but does not automatically mark a rent charge as fully settled.
- **Enforcement Tier**: Stored Procedure (`usp_RecordPayment`) + Running Balance Logic
- **Validation Logic**: When `payment_amount < charge_amount`, payment is allocated against `payment_allocations`. The charge status is set to 'PARTIALLY_PAID', and outstanding balance reflects remaining difference. Charge is only marked 'PAID' when sum of allocations equals amount due.
- **Business Justification**: Accurate financial ledger and delinquency prevention when underpaid.
- **Test Coverage**: `test_br04_partial_payment.py`, integration test
- **Status**: `DEFINED` (Phase 0 Baseline)

### BR-05 — Late fees apply only after the configured grace period.
- **Enforcement Tier**: SQL Function (`fn_CalculateLateFee`) + Nightly Billing Engine
- **Validation Logic**: If `current_date > (due_date + grace_period_days)` AND `outstanding_balance > 0`, calculate late fee according to lease policy (e.g. 5% of unpaid amount or flat ₹500). If within grace period, fee = 0.00.
- **Business Justification**: Legal compliance with lease agreements and tenant protection laws.
- **Test Coverage**: `test_br05_late_fee_grace.py`, SQL function unit test
- **Status**: `DEFINED` (Phase 0 Baseline)

### BR-06 — Delinquency status depends on outstanding amount and overdue duration.
- **Enforcement Tier**: SQL Stored Procedure (`usp_GetDelinquencyReport`) + Delinquency Evaluator
- **Validation Logic**: Tenants with unpaid balances past due date + grace period are categorized into aging buckets: Current (0 days), 1–30 Days, 31–60 Days, 61–90 Days, 90+ Days. Status changes to 'DELINQUENT' when overdue > 30 days.
- **Business Justification**: Operational collection prioritization and aging analysis.
- **Test Coverage**: `test_br06_delinquency_status.py`, reporting test
- **Status**: `DEFINED` (Phase 0 Baseline)

### BR-07 — A terminated lease cannot generate new rent charges.
- **Enforcement Tier**: Stored Procedure (`usp_GenerateMonthlyRent`)
- **Validation Logic**: The monthly rent generation batch only queries `status = 'ACTIVE'`. Terminated, Draft, or Expired leases are strictly filtered out using `WHERE status = 'ACTIVE' AND start_date <= :billing_month_end`.
- **Business Justification**: Prevent illegal billing and phantom revenue generation.
- **Test Coverage**: `test_br07_terminated_lease.py`, monthly billing test
- **Status**: `DEFINED` (Phase 0 Baseline)

### BR-08 — A closed maintenance request cannot receive further work without reopening.
- **Enforcement Tier**: Database Trigger (`trg_PreventWorkOrderOnClosedMaintenance`) + API Service
- **Validation Logic**: Attempting to insert a `work_order` for a maintenance request where `status = 'CLOSED'` is blocked by a trigger with error message 'Cannot attach work order to a closed maintenance request. Reopen the request first.'
- **Business Justification**: Ensure accountability and prevent unauthorized post-facto expenses.
- **Test Coverage**: `test_br08_closed_maintenance.py`, DB trigger test
- **Status**: `DEFINED` (Phase 0 Baseline)

### BR-09 — Only authorized roles can access financial data.
- **Enforcement Tier**: Server-side RBAC Guard + Row-Level Security / API Dependencies
- **Validation Logic**: Endpoints exposing rent, payments, balance, expenses, and financial reports verify user role (`ADMIN`, `PROPERTY_MANAGER`, `ACCOUNTANT`). `TENANT` only accesses their own ledger. `MAINTENANCE` and `LEASING` cannot access financial summaries.
- **Business Justification**: Confidentiality and role segregation.
- **Test Coverage**: `test_br09_financial_auth.py`, API security test
- **Status**: `DEFINED` (Phase 0 Baseline)

### BR-10 — Payment processing must be atomic.
- **Enforcement Tier**: SQL Transaction (`BEGIN / COMMIT / ROLLBACK`) in `usp_RecordPayment`
- **Validation Logic**: Payment processing executes steps 1–6 (validate lease, validate payment, insert payment, allocate to charges, update balance ledger, record audit event) inside an atomic transaction. Any runtime error or constraint failure triggers immediate `ROLLBACK`.
- **Business Justification**: Prevent financial corruption, orphan payment records, and ledger desynchronization.
- **Test Coverage**: `test_br10_atomic_payment.py`, failure rollback simulation test
- **Status**: `DEFINED` (Phase 0 Baseline)
