-- ======================================================================
-- PropLedger Phase 9: Automated Database Constraint & Trigger Validation
-- Target: PostgreSQL 16
-- Purpose: Verify check constraints, referential integrity, and trigger rollbacks.
-- ======================================================================

DO $$
BEGIN
    -- 1. Test chk_rc_amount: Rent charge must be non-negative
    BEGIN
        INSERT INTO rent_charges (lease_id, billing_month, billing_year, charge_date, due_date, charge_amount, amount_paid, status)
        VALUES (1, 1, 2026, '2026-01-01', '2026-01-05', -500.00, 0.00, 'PENDING');
        RAISE EXCEPTION 'FAILURE: Negative rent charge was unexpectedly accepted!';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'SUCCESS: chk_rc_amount successfully rejected negative rent charge.';
    END;

    -- 2. Test chk_payment_amount: Payment must be strictly positive
    BEGIN
        INSERT INTO payments (lease_id, payment_date, amount, payment_method, recorded_by)
        VALUES (1, CURRENT_DATE, 0.00, 'ACH', 32);
        RAISE EXCEPTION 'FAILURE: Zero payment amount was unexpectedly accepted!';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'SUCCESS: chk_payment_amount successfully rejected zero payment amount.';
    END;

    -- 3. Test chk_allocation_amount: Allocation must be strictly positive
    BEGIN
        INSERT INTO payment_allocations (payment_id, charge_id, allocated_amount)
        VALUES (1, 1, -10.00);
        RAISE EXCEPTION 'FAILURE: Negative allocation was unexpectedly accepted!';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'SUCCESS: chk_allocation_amount successfully rejected negative allocation.';
    END;

    -- 4. Test chk_rc_month: Month must be between 1 and 12
    BEGIN
        INSERT INTO rent_charges (lease_id, billing_month, billing_year, charge_date, due_date, charge_amount, amount_paid, status)
        VALUES (1, 13, 2026, '2026-01-01', '2026-01-05', 1000.00, 0.00, 'PENDING');
        RAISE EXCEPTION 'FAILURE: Month 13 was unexpectedly accepted!';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'SUCCESS: chk_rc_month successfully rejected invalid billing month 13.';
    END;

    -- 5. Test chk_rc_due_date: Due date cannot be earlier than charge date
    BEGIN
        INSERT INTO rent_charges (lease_id, billing_month, billing_year, charge_date, due_date, charge_amount, amount_paid, status)
        VALUES (1, 1, 2026, '2026-01-10', '2026-01-05', 1000.00, 0.00, 'PENDING');
        RAISE EXCEPTION 'FAILURE: Due date before charge date was unexpectedly accepted!';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'SUCCESS: chk_rc_due_date successfully rejected due date prior to charge date.';
    END;

    -- 6. Test trg_paymentauditinsert: Verify trigger fires and writes audit row
    DECLARE
        v_test_payment_id BIGINT;
        v_audit_count INT;
    BEGIN
        INSERT INTO payments (lease_id, payment_date, amount, payment_method, reference_number, recorded_by)
        VALUES (1, CURRENT_DATE, 100.00, 'ACH', 'TRIGGER-TEST-REF', 32)
        RETURNING payment_id INTO v_test_payment_id;

        SELECT COUNT(*) INTO v_audit_count 
        FROM payment_audit 
        WHERE payment_id = v_test_payment_id;

        IF v_audit_count = 1 THEN
            RAISE NOTICE 'SUCCESS: trg_paymentauditinsert successfully wrote audit record for payment %.', v_test_payment_id;
        ELSE
            RAISE EXCEPTION 'FAILURE: Payment audit row was NOT created by trigger!';
        END IF;

        -- Clean up test payment
        DELETE FROM payment_audit WHERE payment_id = v_test_payment_id;
        DELETE FROM payments WHERE payment_id = v_test_payment_id;
    END;

    RAISE NOTICE 'ALL DATABASE CONSTRAINT AND TRIGGER TESTS PASSED WITH ZERO ERRORS.';
END $$;
