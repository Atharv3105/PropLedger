-- ======================================================================
-- Procedure: usp_GenerateMonthlyRent
-- Description: Batch generates rent charges for all active leases for a given month
-- PRD Reference: Part J, Part W (BR-07)
-- Techniques: NOT EXISTS subquery, Batch INSERT with ON CONFLICT
-- ======================================================================

CREATE OR REPLACE FUNCTION usp_GenerateMonthlyRent(
    p_billing_month INT,
    p_billing_year INT
) RETURNS TABLE (
    charges_created INT,
    total_amount_billed NUMERIC(14, 2)
) AS $$
DECLARE
    v_charge_date DATE;
    v_due_date DATE;
    v_count INT := 0;
    v_total NUMERIC(14, 2) := 0.00;
BEGIN
    v_charge_date := MAKE_DATE(p_billing_year, p_billing_month, 1);
    v_due_date := MAKE_DATE(p_billing_year, p_billing_month, 5);

    -- Rule BR-07: Terminated leases cannot generate rent charges. Only ACTIVE / EXPIRING valid leases.
    WITH inserted AS (
        INSERT INTO rent_charges (lease_id, billing_month, billing_year, charge_date, due_date, charge_amount, status, created_by)
        SELECT 
            l.lease_id,
            p_billing_month,
            p_billing_year,
            v_charge_date,
            v_due_date,
            l.monthly_rent,
            'PENDING',
            l.created_by
        FROM leases l
        WHERE l.status IN ('ACTIVE', 'EXPIRING')
          AND l.start_date <= v_due_date
          AND l.end_date >= v_charge_date
          -- Prevent duplicate billing for the same month/year
          AND NOT EXISTS (
              SELECT 1 FROM rent_charges rc 
              WHERE rc.lease_id = l.lease_id 
                AND rc.billing_month = p_billing_month 
                AND rc.billing_year = p_billing_year
          )
        RETURNING charge_amount
    )
    SELECT COUNT(*), COALESCE(SUM(charge_amount), 0.00)
    INTO v_count, v_total
    FROM inserted;

    RETURN QUERY SELECT v_count, v_total;
END;
$$ LANGUAGE plpgsql;
