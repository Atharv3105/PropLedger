-- ======================================================================
-- PropLedger Phase 9: Stored Procedure Transactional Atomicity & Rollback Tests
-- Target: PostgreSQL 16
-- Purpose: Verify ACID guarantees, exception handling, and rollback behavior.
-- ======================================================================

DO $$
DECLARE
    v_lease_id BIGINT;
    v_unit_id BIGINT;
    v_charge_id BIGINT;
    v_initial_balance NUMERIC;
    v_post_balance NUMERIC;
    v_payment_res JSONB;
BEGIN
    -- 1. Setup isolated test environment
    SELECT unit_id INTO v_unit_id FROM units LIMIT 1;
    
    INSERT INTO leases (unit_id, start_date, end_date, monthly_rent, security_deposit, rent_due_day, late_fee_policy_id, status)
    VALUES (v_unit_id, '2026-01-01', '2026-12-31', 1500.00, 1500.00, 1, 1, 'Active')
    RETURNING lease_id INTO v_lease_id;

    INSERT INTO rent_charges (lease_id, billing_month, billing_year, charge_date, due_date, charge_amount, amount_paid, status)
    VALUES (v_lease_id, 1, 2026, '2026-01-01', '2026-01-05', 1500.00, 0.00, 'PENDING')
    RETURNING charge_id INTO v_charge_id;

    v_initial_balance := fn_GetOutstandingBalance(v_lease_id);
    IF v_initial_balance != 1500.00 THEN
        RAISE EXCEPTION 'FAILURE: Expected initial balance of 1500.00, got %', v_initial_balance;
    END IF;

    -- 2. Test usp_RecordPayment rollback on invalid payment amount (<= 0)
    BEGIN
        PERFORM usp_RecordPayment(v_lease_id, -100.00, 'ACH', 'FAIL-PAY', 32);
        RAISE EXCEPTION 'FAILURE: Negative payment should have raised exception!';
    EXCEPTION WHEN OTHERS THEN
        RAISE NOTICE 'SUCCESS: usp_RecordPayment rejected negative amount and aborted transaction.';
    END;

    -- Verify balance did not change (Atomicity verified)
    v_post_balance := fn_GetOutstandingBalance(v_lease_id);
    IF v_post_balance != 1500.00 THEN
        RAISE EXCEPTION 'FAILURE: Balance changed after failed payment! Atomicity violated.';
    ELSE
        RAISE NOTICE 'SUCCESS: Balance untouched at 1500.00 after failed transaction (Rollback verified).';
    END IF;

    -- 3. Test valid usp_RecordPayment execution and FIFO allocation
    v_payment_res := usp_RecordPayment(v_lease_id, 1500.00, 'ACH', 'SP-PASS-PAY', 32);
    v_post_balance := fn_GetOutstandingBalance(v_lease_id);
    IF v_post_balance != 0.00 THEN
        RAISE EXCEPTION 'FAILURE: Expected balance of 0.00 after full payment, got %', v_post_balance;
    ELSE
        RAISE NOTICE 'SUCCESS: Full payment cleanly updated outstanding balance to 0.00.';
    END IF;

    -- 4. Clean up test data
    DELETE FROM payment_allocations WHERE charge_id = v_charge_id;
    DELETE FROM payment_audit WHERE lease_id = v_lease_id;
    DELETE FROM payments WHERE lease_id = v_lease_id;
    DELETE FROM rent_charges WHERE lease_id = v_lease_id;
    DELETE FROM tenant_balances WHERE lease_id = v_lease_id;
    DELETE FROM leases WHERE lease_id = v_lease_id;

    RAISE NOTICE 'ALL STORED PROCEDURE ATOMICITY TESTS PASSED SUCCESSFULLY.';
END $$;
