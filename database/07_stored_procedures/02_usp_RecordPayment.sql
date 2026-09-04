-- ======================================================================
-- Procedure: usp_RecordPayment
-- Description: Transactional payment recording with FIFO allocation & balance updates
-- PRD Reference: Part J, Part K, Part W (BR-03, BR-04, BR-10)
-- Techniques: Transaction integrity, FIFO cursor loop, Running balance maintenance
-- ======================================================================

CREATE OR REPLACE FUNCTION usp_RecordPayment(
    p_lease_id BIGINT,
    p_amount NUMERIC(12, 2),
    p_payment_method VARCHAR(50),
    p_reference_number VARCHAR(100),
    p_recorded_by BIGINT
) RETURNS JSONB AS $$
DECLARE
    v_lease_status VARCHAR(50);
    v_payment_id BIGINT;
    v_remaining_funds NUMERIC(12, 2);
    v_charge_record RECORD;
    v_allocate_amt NUMERIC(12, 2);
    v_tenant_id BIGINT;
    v_new_balance NUMERIC(14, 2);
BEGIN
    -- Validate payment amount
    IF p_amount <= 0.00 THEN
        RAISE EXCEPTION 'Rule Check Failed: Payment amount must be strictly positive (received: %)', p_amount;
    END IF;

    -- Rule BR-03: Payment cannot be recorded against an invalid or terminated lease
    SELECT status INTO v_lease_status FROM leases WHERE lease_id = p_lease_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Rule BR-03 Violation: Lease ID % does not exist', p_lease_id;
    END IF;
    IF v_lease_status IN ('TERMINATED', 'CANCELLED') THEN
        RAISE EXCEPTION 'Rule BR-03 Violation: Cannot record payment against lease with status %', v_lease_status;
    END IF;

    -- Step 1: Insert Payment
    INSERT INTO payments (lease_id, payment_date, amount, payment_method, reference_number, recorded_by)
    VALUES (p_lease_id, CURRENT_DATE, p_amount, p_payment_method, p_reference_number, p_recorded_by)
    RETURNING payment_id INTO v_payment_id;

    -- Step 2: FIFO Allocation across unpaid or partially paid rent charges
    v_remaining_funds := p_amount;

    FOR v_charge_record IN 
        SELECT charge_id, (charge_amount - amount_paid) AS balance_due
        FROM rent_charges
        WHERE lease_id = p_lease_id AND status != 'PAID'
        ORDER BY charge_date ASC, charge_id ASC
    LOOP
        EXIT WHEN v_remaining_funds <= 0.00;

        v_allocate_amt := LEAST(v_remaining_funds, v_charge_record.balance_due);

        -- Insert allocation
        INSERT INTO payment_allocations (payment_id, charge_id, allocated_amount)
        VALUES (v_payment_id, v_charge_record.charge_id, v_allocate_amt);

        -- Update rent charge
        UPDATE rent_charges
        SET amount_paid = amount_paid + v_allocate_amt,
            status = CASE 
                WHEN (amount_paid + v_allocate_amt) >= charge_amount THEN 'PAID'
                ELSE 'PARTIALLY_PAID'
            END,
            modified_at = CURRENT_TIMESTAMP
        WHERE charge_id = v_charge_record.charge_id;

        v_remaining_funds := v_remaining_funds - v_allocate_amt;
    END LOOP;

    -- Step 3: Update running tenant balance
    SELECT tenant_id INTO v_tenant_id 
    FROM lease_tenants 
    WHERE lease_id = p_lease_id AND is_primary = TRUE 
    LIMIT 1;

    v_new_balance := fn_GetOutstandingBalance(p_lease_id);

    INSERT INTO tenant_balances (tenant_id, lease_id, total_paid, outstanding_balance, last_updated)
    VALUES (
        COALESCE(v_tenant_id, 1),
        p_lease_id,
        p_amount,
        v_new_balance,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (lease_id) DO UPDATE
    SET total_paid = tenant_balances.total_paid + EXCLUDED.total_paid,
        outstanding_balance = EXCLUDED.outstanding_balance,
        last_updated = CURRENT_TIMESTAMP;

    RETURN jsonb_build_object(
        'payment_id', v_payment_id,
        'lease_id', p_lease_id,
        'amount', p_amount,
        'unallocated_credit', v_remaining_funds,
        'outstanding_balance', v_new_balance,
        'status', 'SUCCESS'
    );
END;
$$ LANGUAGE plpgsql;
