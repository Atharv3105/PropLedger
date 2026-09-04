-- ======================================================================
-- View: vw_MonthlyRentCollectionPivot
-- Description: PIVOT Analysis cross-tabulating Property x Monthly Rent Collection
-- PRD Reference: Part J (PIVOT demonstration)
-- Techniques: Conditional Aggregation PIVOT across 12 calendar months
-- ======================================================================

CREATE OR REPLACE VIEW vw_MonthlyRentCollectionPivot AS
SELECT 
    p.property_id,
    p.property_code,
    p.name AS property_name,
    rc.billing_year,
    ROUND(SUM(CASE WHEN rc.billing_month = 1  THEN rc.amount_paid ELSE 0.00 END), 2) AS jan_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 2  THEN rc.amount_paid ELSE 0.00 END), 2) AS feb_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 3  THEN rc.amount_paid ELSE 0.00 END), 2) AS mar_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 4  THEN rc.amount_paid ELSE 0.00 END), 2) AS apr_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 5  THEN rc.amount_paid ELSE 0.00 END), 2) AS may_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 6  THEN rc.amount_paid ELSE 0.00 END), 2) AS jun_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 7  THEN rc.amount_paid ELSE 0.00 END), 2) AS jul_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 8  THEN rc.amount_paid ELSE 0.00 END), 2) AS aug_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 9  THEN rc.amount_paid ELSE 0.00 END), 2) AS sep_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 10 THEN rc.amount_paid ELSE 0.00 END), 2) AS oct_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 11 THEN rc.amount_paid ELSE 0.00 END), 2) AS nov_collected,
    ROUND(SUM(CASE WHEN rc.billing_month = 12 THEN rc.amount_paid ELSE 0.00 END), 2) AS dec_collected,
    ROUND(SUM(rc.amount_paid), 2) AS annual_total_collected
FROM properties p
INNER JOIN buildings b ON p.property_id = b.property_id
INNER JOIN units u ON b.building_id = u.building_id
INNER JOIN leases l ON u.unit_id = l.unit_id
INNER JOIN rent_charges rc ON l.lease_id = rc.lease_id
GROUP BY p.property_id, p.property_code, p.name, rc.billing_year;
