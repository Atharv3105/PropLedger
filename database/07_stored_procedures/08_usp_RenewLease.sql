-- ======================================================================
-- Procedure: usp_RenewLease
-- Description: Executes lease renewal, linking predecessor lease and rolling deposits
-- PRD Reference: Part I (Module 4), Part W (BR-02)
-- ======================================================================

CREATE OR REPLACE FUNCTION usp_RenewLease(
    p_lease_id BIGINT,
    p_new_start_date DATE,
    p_new_end_date DATE,
    p_new_monthly_rent NUMERIC(12, 2),
    p_recorded_by BIGINT
) RETURNS JSONB AS $$
DECLARE
    v_old_status VARCHAR(50);
    v_unit_id BIGINT;
    v_sec_deposit NUMERIC(12, 2);
    v_rent_due_day INT;
    v_late_policy_id BIGINT;
    v_new_lease_id BIGINT;
    v_tenant_record RECORD;
BEGIN
    -- Validate dates (Rule BR-02)
    IF p_new_start_date > p_new_end_date THEN
        RAISE EXCEPTION 'Rule BR-02 Violation: Lease start date (%) cannot be after end date (%)', p_new_start_date, p_new_end_date;
    END IF;

    -- Fetch existing lease details
    SELECT unit_id, status, security_deposit, rent_due_day, late_fee_policy_id
    INTO v_unit_id, v_old_status, v_sec_deposit, v_rent_due_day, v_late_policy_id
    FROM leases
    WHERE lease_id = p_lease_id;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Lease with ID % does not exist', p_lease_id;
    END IF;

    IF v_old_status = 'TERMINATED' THEN
        RAISE EXCEPTION 'Cannot renew a terminated lease (ID %)', p_lease_id;
    END IF;

    -- Step 1: Insert New Renewed Lease
    INSERT INTO leases (
        unit_id, start_date, end_date, monthly_rent, security_deposit,
        rent_due_day, late_fee_policy_id, status, renewal_status,
        predecessor_lease_id, notes, created_by
    ) VALUES (
        v_unit_id, p_new_start_date, p_new_end_date, p_new_monthly_rent, v_sec_deposit,
        v_rent_due_day, v_late_policy_id, 'ACTIVE', 'RENEWED',
        p_lease_id, 'Renewal of lease #' || p_lease_id::TEXT, p_recorded_by
    )
    RETURNING lease_id INTO v_new_lease_id;

    -- Step 2: Associate existing tenants with the new lease
    FOR v_tenant_record IN
        SELECT tenant_id, is_primary
        FROM lease_tenants
        WHERE lease_id = p_lease_id
    LOOP
        INSERT INTO lease_tenants (lease_id, tenant_id, is_primary)
        VALUES (v_new_lease_id, v_tenant_record.tenant_id, v_tenant_record.is_primary)
        ON CONFLICT DO NOTHING;
    END LOOP;

    -- Step 3: Rollover security deposit record
    UPDATE security_deposits
    SET lease_id = v_new_lease_id,
        modified_at = CURRENT_TIMESTAMP,
        modified_by = p_recorded_by
    WHERE lease_id = p_lease_id;

    -- Step 4: Update status on predecessor lease
    UPDATE leases
    SET status = 'RENEWED',
        renewal_status = 'RENEWED',
        modified_at = CURRENT_TIMESTAMP,
        modified_by = p_recorded_by
    WHERE lease_id = p_lease_id;

    -- Step 5: Log into lease_history
    INSERT INTO lease_history (lease_id, action, old_rent, new_rent, old_status, new_status, changed_by, notes)
    VALUES (
        p_lease_id, 'RENEWED', NULL, p_new_monthly_rent, v_old_status, 'RENEWED',
        p_recorded_by, 'Renewed into successor lease #' || v_new_lease_id::TEXT
    );

    RETURN jsonb_build_object(
        'status', 'SUCCESS',
        'old_lease_id', p_lease_id,
        'new_lease_id', v_new_lease_id,
        'new_start_date', p_new_start_date,
        'new_end_date', p_new_end_date,
        'new_monthly_rent', p_new_monthly_rent
    );
END;
$$ LANGUAGE plpgsql;
