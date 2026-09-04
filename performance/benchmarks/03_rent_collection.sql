-- Query 3: Monthly Rent Collection Efficiency Aggregation
-- Requirements: PL-134
-- Aggregates 100k+ charges by billing year, month, and property
SELECT 
    rc.billing_year,
    rc.billing_month,
    p.property_id,
    p.name AS property_name,
    COUNT(rc.charge_id) AS total_billed_charges,
    SUM(rc.charge_amount) AS total_amount_billed,
    SUM(rc.amount_paid) AS total_amount_collected,
    SUM(rc.charge_amount - rc.amount_paid) AS total_outstanding,
    ROUND(SUM(rc.amount_paid) / NULLIF(SUM(rc.charge_amount), 0) * 100, 2) AS collection_rate_pct,
    COUNT(CASE WHEN rc.status = 'PAID' THEN 1 END) AS fully_paid_count,
    COUNT(CASE WHEN rc.status = 'PARTIALLY_PAID' THEN 1 END) AS partial_count,
    COUNT(CASE WHEN rc.status = 'OVERDUE' THEN 1 END) AS overdue_count
FROM rent_charges rc
JOIN leases l ON l.lease_id = rc.lease_id
JOIN units u ON u.unit_id = l.unit_id
JOIN buildings b ON b.building_id = u.building_id
JOIN properties p ON p.property_id = b.property_id
WHERE rc.billing_year = 2025
GROUP BY rc.billing_year, rc.billing_month, p.property_id, p.name
ORDER BY rc.billing_year DESC, rc.billing_month DESC, total_amount_billed DESC;
