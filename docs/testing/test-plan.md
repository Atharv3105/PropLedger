# PropLedger Master Quality Assurance & Test Plan

- **Requirement IDs**: `PL-138`, `PL-139`, `PL-140`, `PL-141`
- **Scope**: Enterprise Test Pyramid (Unit, Integration, Database, Reporting)
- **Target OS**: Cross-Platform (Linux / macOS / Windows)
- **Test Runners**: `pytest 9.1`, `psycopg2`, `pypdf`, `openpyxl`

---

## 1. Quality Assurance Architecture & Test Pyramid

PropLedger enforces a rigorous four-tier testing hierarchy to guarantee transactional integrity, mathematical correctness, and high-performance reporting:

```
                  ▲
                 / \
                /   \
               /     \
              /  UI   \       Phase 5: React Component & Navigation Tests
             /  E2E    \      
            /───────────\
           /   Report    \    Phase 9 (PL-141): OpenPyXL Formula & PDF Fidelity Tests
          /  Validation   \   
         /─────────────────\
        /    Integration    \ Phase 9 (PL-139): Critical Financial Lifecycle (API -> DB)
       /─────────────────────\
      /   Database Integrity  \ Phase 9 (PL-140): Check Constraints, Triggers, SP Rollbacks
     /─────────────────────────\
    /        Unit Tests         \ Phase 9 (PL-138): Late Fees, Balance Derivation, Lease State Machine
   /─────────────────────────────\
```

---

## 2. Business Rules & Test Coverage Mapping

Every PRD business rule is mapped to dedicated test suites:

| Rule ID | Domain Rule Description | Verification Level | Test Module | Evidence / Assertion |
|---|---|---|---|---|
| **BR-01** | Running Tenant Balance Derivation | Unit & Integration | `test_business_logic_unit.py` | `derive_tenant_balance()` matches double-entry equation. |
| **BR-02** | Late Fee Calculation Policy | Unit | `test_business_logic_unit.py` | Flat, percentage, and capped daily accrual models tested on exact date boundaries. |
| **BR-03** | Active Tenancy Enforcement for Payments | Database & API | `01_constraints_and_triggers.sql`, `test_financial_lifecycle_integration.py` | Terminated and invalid leases reject payments. |
| **BR-04** | Delinquency Aging Buckets (30/60/90+) | Unit & API | `test_business_logic_unit.py`, `test_delinquency_report_endpoint` | `classify_delinquency_aging()` accurately groups past due days. |
| **BR-05** | Grace Period Threshold Compliance | Unit | `test_business_logic_unit.py` | Payments within grace period incur strictly $0.00 fee. |
| **BR-06** | Lease Lifecycle State Machine Transitions | Unit & DB | `test_business_logic_unit.py`, `02_stored_procedure_atomicity.sql` | Illegal state changes (e.g. `Terminated` $\to$ `Active`) raise `InvalidStateTransitionError`. |
| **BR-07** | FIFO Rent Allocation | Integration & SP | `test_payment_recording_with_fifo_allocation` | Atomic waterfall allocation across oldest unpaid charges. |
| **BR-08** | Non-Negative Numeric Integrity | Database Constraints | `01_constraints_and_triggers.sql` | `chk_rc_amount`, `chk_payment_amount`, `chk_allocation_amount` strictly reject `< 0`. |
| **BR-09** | Payment Audit Trail Generation | Database Triggers | `01_constraints_and_triggers.sql` | `trg_paymentauditinsert` automatically populates `payment_audit`. |
| **BR-10** | Export Format & Formula Fidelity | Report Validation | `test_report_exports_validation.py` | OpenPyXL workbooks contain valid `=SUM()` formulas and non-string numbers. |

---

## 3. Test Suites & Execution Instructions

### 3.1 Tier 1: Business Logic Unit Tests (`PL-138`)
Fast, pure Python unit tests validating financial algorithms:
```bash
cd D:/PropLedger/backend/fastapi-api
python -m pytest tests/unit/ -v
```

### 3.2 Tier 2: End-to-End Financial Lifecycle Integration Tests (`PL-139`)
Executes the full critical path (Lease Inception $	o$ Rent Charge $	o$ Partial Payment with FIFO $	o$ Running Balance $	o$ Late Fee $	o$ Delinquency $	o$ Legal Escalation):
```bash
cd D:/PropLedger/backend/fastapi-api
python -m pytest tests/integration/ -v
```

### 3.3 Tier 3: Database Constraints, Triggers & SP Atomicity Tests (`PL-140`)
Executes SQL test harness validating ACID transactions, rollbacks, and check constraints:
```bash
python D:/PropLedger/database/11_test_scripts/run_all_tests.py
```

### 3.4 Tier 4: Report Export Fidelity & Formula Tests (`PL-141`)
Validates OpenPyXL Excel formula calculation, header styling, and ReportLab `%PDF-` binary structure:
```bash
cd D:/PropLedger/backend/fastapi-api
python -m pytest tests/reports/ -v
```

### 3.5 Complete Master Regression Test Command
```bash
cd D:/PropLedger/backend/fastapi-api
python -m pytest tests/ -v
```
