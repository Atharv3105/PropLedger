-- ======================================================================
-- Function: fn_CalculateLateFee
-- Description: Calculates policy-driven late fee respecting grace period and caps
-- PRD Reference: Part J, Part W (BR-05)
-- ======================================================================

CREATE OR REPLACE FUNCTION fn_CalculateLateFee(
    p_lease_id BIGINT,
    p_unpaid_amount NUMERIC,
    p_days_overdue INT
) RETURNS NUMERIC AS $$
DECLARE
    v_grace_days INT;
    v_fee_type VARCHAR(20);
    v_flat_amount NUMERIC(10, 2);
    v_fee_pct NUMERIC(5, 2);
    v_max_cap NUMERIC(10, 2);
    v_calculated_fee NUMERIC(10, 2) := 0.00;
BEGIN
    -- Return 0 if balance is already cleared or non-positive
    IF p_unpaid_amount <= 0.00 OR p_days_overdue <= 0 THEN
        RETURN 0.00;
    END IF;

    -- Fetch policy linked to lease
    SELECT 
        lfp.grace_period_days, lfp.fee_type, lfp.fee_amount, lfp.fee_percentage, lfp.max_fee_cap
    INTO 
        v_grace_days, v_fee_type, v_flat_amount, v_fee_pct, v_max_cap
    FROM leases l
    INNER JOIN late_fee_policies lfp ON l.late_fee_policy_id = lfp.policy_id
    WHERE l.lease_id = p_lease_id;

    -- If no policy found, default to 5 grace days and 5% fee
    IF NOT FOUND THEN
        v_grace_days := 5;
        v_fee_type := 'PERCENTAGE';
        v_flat_amount := 500.00;
        v_fee_pct := 5.00;
        v_max_cap := 2500.00;
    END IF;

    -- Rule BR-05: Late fees apply only after configured grace period
    IF p_days_overdue <= v_grace_days THEN
        RETURN 0.00;
    END IF;

    IF v_fee_type = 'FLAT' THEN
        v_calculated_fee := v_flat_amount;
    ELSE
        v_calculated_fee := ROUND((v_fee_pct / 100.0) * p_unpaid_amount, 2);
        IF v_max_cap IS NOT NULL AND v_calculated_fee > v_max_cap THEN
            v_calculated_fee := v_max_cap;
        END IF;
    END IF;

    RETURN v_calculated_fee;
END;
$$ LANGUAGE plpgsql STABLE;
