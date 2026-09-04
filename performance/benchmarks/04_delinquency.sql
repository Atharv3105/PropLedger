-- Query 4: Portfolio Delinquency Aging Aggregation under Heavy Volume
-- Requirements: PL-135
-- Scans and aggregates overdue/unpaid charges into 30/60/90+ day aging buckets
SELECT 
    p.property_id,
    p.name AS property_name,
    l.lease_id,
    t.first_name || ' ' || t.last_name AS tenant_name,
    u.unit_number,
    SUM(rc.charge_amount - rc.amount_paid) AS total_delinquent_balance,
    SUM(CASE WHEN (CURRENT_DATE - rc.due_date) BETWEEN 1 AND 30 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END) AS aging_1_30_days,
    SUM(CASE WHEN (CURRENT_DATE - rc.due_date) BETWEEN 31 AND 60 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END) AS aging_31_60_days,
    SUM(CASE WHEN (CURRENT_DATE - rc.due_date) BETWEEN 61 AND 90 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END) AS aging_61_90_days,
    SUM(CASE WHEN (CURRENT_DATE - rc.due_date) > 90 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END) AS aging_over_90_days,
    MAX(CURRENT_DATE - rc.due_date) AS max_days_past_due
FROM rent_charges rc
JOIN leases l ON l.lease_id = rc.lease_id
JOIN units u ON u.unit_id = l.unit_id
JOIN buildings b ON b.building_id = u.building_id
JOIN properties p ON p.property_id = b.property_id
LEFT JOIN lease_tenants lt ON lt.lease_id = l.lease_id AND lt.is_primary = TRUE
LEFT JOIN tenants t ON t.tenant_id = lt.tenant_id
WHERE rc.status IN ('PENDING', 'PARTIALLY_PAID', 'OVERDUE')
  AND rc.charge_amount > rc.amount_paid
  AND rc.due_date < CURRENT_DATE
GROUP BY p.property_id, p.name, l.lease_id, t.first_name, t.last_name, u.unit_number
HAVING SUM(rc.charge_amount - rc.amount_paid) > 0
ORDER BY total_delinquent_balance DESC, max_days_past_due DESC;
