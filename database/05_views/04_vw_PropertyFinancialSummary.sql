-- ======================================================================
-- View: vw_PropertyFinancialSummary
-- Description: Comprehensive property financial rollup (Revenue, Expenses, NOI)
-- PRD Reference: Part J, Part P (Report 10), Module 9
-- Techniques: Subqueries, Multi-table Aggregation, Arithmetic Expressions
-- ======================================================================

CREATE OR REPLACE VIEW vw_PropertyFinancialSummary AS
SELECT 
    p.property_id,
    p.property_code,
    p.name AS property_name,
    p.property_type,
    p.city,
    o.company_name AS owner_name,
    COALESCE(rev.billed_rent, 0.00) AS total_billed_rent,
    COALESCE(rev.collected_rent, 0.00) AS total_collected_rent,
    COALESCE(rev.total_late_fees, 0.00) AS total_late_fees_collected,
    (COALESCE(rev.collected_rent, 0.00) + COALESCE(rev.total_late_fees, 0.00)) AS total_operating_revenue,
    COALESCE(exp.total_expenses, 0.00) AS total_operating_expenses,
    ((COALESCE(rev.collected_rent, 0.00) + COALESCE(rev.total_late_fees, 0.00)) - COALESCE(exp.total_expenses, 0.00)) AS net_operating_income,
    ROUND(
        CASE 
            WHEN COALESCE(rev.billed_rent, 0.00) > 0 THEN 
                (COALESCE(rev.collected_rent, 0.00) / rev.billed_rent) * 100.0 
            ELSE 0.0 
        END, 2
    ) AS collection_percentage
FROM properties p
INNER JOIN owners o ON p.owner_id = o.owner_id
LEFT JOIN (
    SELECT 
        b.property_id,
        SUM(rc.charge_amount) AS billed_rent,
        SUM(rc.amount_paid) AS collected_rent,
        SUM(COALESCE(lf.fee_amount, 0.00)) AS total_late_fees
    FROM rent_charges rc
    INNER JOIN leases l ON rc.lease_id = l.lease_id
    INNER JOIN units u ON l.unit_id = u.unit_id
    INNER JOIN buildings b ON u.building_id = b.building_id
    LEFT JOIN late_fees lf ON rc.charge_id = lf.charge_id AND lf.is_waived = FALSE
    GROUP BY b.property_id
) rev ON p.property_id = rev.property_id
LEFT JOIN (
    SELECT property_id, SUM(amount) AS total_expenses
    FROM expenses
    GROUP BY property_id
) exp ON p.property_id = exp.property_id;
