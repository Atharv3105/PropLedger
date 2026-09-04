-- ======================================================================
-- Function: fn_GetOutstandingBalance
-- Description: Computes net scalar outstanding balance for a given lease
-- PRD Reference: Part J, Module 5
-- ======================================================================

CREATE OR REPLACE FUNCTION fn_GetOutstandingBalance(
    p_lease_id BIGINT
) RETURNS NUMERIC AS $$
DECLARE
    v_total_charges NUMERIC(14, 2) := 0.00;
    v_total_fees NUMERIC(14, 2) := 0.00;
    v_total_paid NUMERIC(14, 2) := 0.00;
BEGIN
    SELECT COALESCE(SUM(charge_amount), 0.00)
    INTO v_total_charges
    FROM rent_charges
    WHERE lease_id = p_lease_id AND status != 'CANCELLED';

    SELECT COALESCE(SUM(lf.fee_amount), 0.00)
    INTO v_total_fees
    FROM late_fees lf
    INNER JOIN rent_charges rc ON lf.charge_id = rc.charge_id
    WHERE rc.lease_id = p_lease_id AND lf.is_waived = FALSE;

    SELECT COALESCE(SUM(amount), 0.00)
    INTO v_total_paid
    FROM payments
    WHERE lease_id = p_lease_id;

    RETURN ROUND(v_total_charges + v_total_fees - v_total_paid, 2);
END;
$$ LANGUAGE plpgsql STABLE;
