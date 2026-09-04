-- ======================================================================
-- Procedure: usp_EscalateToCollection
-- Description: Escalates a severely overdue lease to a formal Collection Case
-- PRD Reference: Part I (Module 6)
-- ======================================================================

CREATE OR REPLACE FUNCTION usp_EscalateToCollection(
    p_lease_id BIGINT,
    p_agent_user_id BIGINT,
    p_initial_notes TEXT DEFAULT 'Account escalated due to delinquency threshold breach'
) RETURNS JSONB AS $$
DECLARE
    v_tenant_id BIGINT;
    v_overdue_amt NUMERIC(12, 2);
    v_days_overdue INT;
    v_case_id BIGINT;
    v_existing_case BIGINT;
BEGIN
    -- Check if active case already exists
    SELECT case_id INTO v_existing_case
    FROM collection_cases
    WHERE lease_id = p_lease_id AND status IN ('OPEN', 'IN_REVIEW', 'PAYMENT_PLAN');

    IF v_existing_case IS NOT NULL THEN
        RETURN jsonb_build_object(
            'status', 'ALREADY_EXISTS',
            'case_id', v_existing_case,
            'message', 'Active collection case already exists for this lease'
        );
    END IF;

    -- Fetch primary tenant
    SELECT tenant_id INTO v_tenant_id
    FROM lease_tenants
    WHERE lease_id = p_lease_id AND is_primary = TRUE
    LIMIT 1;

    -- Calculate unpaid rent & overdue days
    SELECT 
        COALESCE(SUM(charge_amount - amount_paid), 0.00),
        COALESCE(MAX(CURRENT_DATE - due_date), 0)
    INTO v_overdue_amt, v_days_overdue
    FROM rent_charges
    WHERE lease_id = p_lease_id AND status != 'PAID' AND due_date < CURRENT_DATE;

    IF v_overdue_amt <= 0.00 THEN
        RAISE EXCEPTION 'Cannot escalate account with zero overdue balance';
    END IF;

    -- Insert collection case
    INSERT INTO collection_cases (
        lease_id, tenant_id, overdue_amount, days_overdue, status, opened_date, notes, created_by
    ) VALUES (
        p_lease_id, v_tenant_id, v_overdue_amt, v_days_overdue, 'OPEN', CURRENT_DATE, p_initial_notes, p_agent_user_id
    )
    RETURNING case_id INTO v_case_id;

    -- Insert initial collection activity
    INSERT INTO collection_activities (
        case_id, activity_type, activity_date, notes, performed_by
    ) VALUES (
        v_case_id, 'DEMAND_LETTER', CURRENT_TIMESTAMP,
        'First formal collection demand letter issued. Overdue: ' || v_overdue_amt::TEXT, p_agent_user_id
    );

    RETURN jsonb_build_object(
        'status', 'SUCCESS',
        'case_id', v_case_id,
        'lease_id', p_lease_id,
        'tenant_id', v_tenant_id,
        'overdue_amount', v_overdue_amt,
        'days_overdue', v_days_overdue
    );
END;
$$ LANGUAGE plpgsql;
