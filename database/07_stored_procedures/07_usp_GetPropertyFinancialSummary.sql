-- ======================================================================
-- Procedure: usp_GetPropertyFinancialSummary
-- Description: Comprehensive property income, operating expenses, and NOI
-- PRD Reference: Part J, Part P (Report 10)
-- ======================================================================

CREATE OR REPLACE FUNCTION usp_GetPropertyFinancialSummary(
    p_property_id BIGINT DEFAULT NULL,
    p_start_date DATE DEFAULT '2020-01-01',
    p_end_date DATE DEFAULT '2030-12-31'
) RETURNS TABLE (
    property_id BIGINT,
    property_code VARCHAR(50),
    property_name VARCHAR(150),
    city VARCHAR(100),
    billed_rent NUMERIC(14, 2),
    collected_rent NUMERIC(14, 2),
    late_fees NUMERIC(14, 2),
    total_operating_revenue NUMERIC(14, 2),
    operating_expenses NUMERIC(14, 2),
    net_operating_income NUMERIC(14, 2),
    collection_percentage NUMERIC(5, 2)
) AS $$
BEGIN
    RETURN QUERY
    WITH RevenueData AS (
        SELECT 
            b.property_id,
            SUM(rc.charge_amount) AS total_billed,
            SUM(rc.amount_paid) AS total_collected,
            SUM(COALESCE(lf.fee_amount, 0.00)) AS total_late_fees
        FROM rent_charges rc
        INNER JOIN leases l ON rc.lease_id = l.lease_id
        INNER JOIN units u ON l.unit_id = u.unit_id
        INNER JOIN buildings b ON u.building_id = b.building_id
        LEFT JOIN late_fees lf ON rc.charge_id = lf.charge_id AND lf.is_waived = FALSE
        WHERE rc.charge_date BETWEEN p_start_date AND p_end_date
        GROUP BY b.property_id
    ),
    ExpenseData AS (
        SELECT 
            e.property_id,
            SUM(e.amount) AS total_exp
        FROM expenses e
        WHERE e.expense_date BETWEEN p_start_date AND p_end_date
        GROUP BY e.property_id
    )
    SELECT 
        p.property_id,
        p.property_code,
        p.name AS property_name,
        p.city,
        COALESCE(rd.total_billed, 0.00) AS billed_rent,
        COALESCE(rd.total_collected, 0.00) AS collected_rent,
        COALESCE(rd.total_late_fees, 0.00) AS late_fees,
        (COALESCE(rd.total_collected, 0.00) + COALESCE(rd.total_late_fees, 0.00)) AS total_operating_revenue,
        COALESCE(ed.total_exp, 0.00) AS operating_expenses,
        ((COALESCE(rd.total_collected, 0.00) + COALESCE(rd.total_late_fees, 0.00)) - COALESCE(ed.total_exp, 0.00)) AS net_operating_income,
        ROUND(
            CASE 
                WHEN COALESCE(rd.total_billed, 0.00) > 0 THEN 
                    (COALESCE(rd.total_collected, 0.00) / rd.total_billed) * 100.0
                ELSE 0.0 
            END, 2
        ) AS collection_percentage
    FROM properties p
    LEFT JOIN RevenueData rd ON p.property_id = rd.property_id
    LEFT JOIN ExpenseData ed ON p.property_id = ed.property_id
    WHERE (p_property_id IS NULL OR p.property_id = p_property_id)
    ORDER BY p.name;
END;
$$ LANGUAGE plpgsql STABLE;
