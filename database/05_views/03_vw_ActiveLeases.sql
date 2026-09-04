-- ======================================================================
-- View: vw_ActiveLeases
-- Description: Detailed active lease roll with SELF JOIN for renewal lineage
-- PRD Reference: Part J (Self Join demonstration), Part P (Report 13)
-- Techniques: INNER JOIN, LEFT JOIN, SELF JOIN
-- ======================================================================

CREATE OR REPLACE VIEW vw_ActiveLeases AS
SELECT 
    l.lease_id,
    l.status AS lease_status,
    l.start_date,
    l.end_date,
    (l.end_date - CURRENT_DATE) AS days_remaining,
    l.monthly_rent,
    l.security_deposit,
    l.rent_due_day,
    l.renewal_status,
    p.property_id,
    p.name AS property_name,
    b.name AS building_name,
    u.unit_id,
    u.unit_number,
    u.unit_type,
    t.tenant_id,
    t.first_name || ' ' || t.last_name AS primary_tenant_name,
    t.email AS primary_tenant_email,
    t.phone AS primary_tenant_phone,
    -- SELF JOIN to show predecessor lease lineage
    pred.lease_id AS predecessor_lease_id,
    pred.start_date AS predecessor_start_date,
    pred.end_date AS predecessor_end_date,
    pred.monthly_rent AS predecessor_monthly_rent
FROM leases l
INNER JOIN units u ON l.unit_id = u.unit_id
INNER JOIN buildings b ON u.building_id = b.building_id
INNER JOIN properties p ON b.property_id = p.property_id
INNER JOIN lease_tenants lt ON l.lease_id = lt.lease_id AND lt.is_primary = TRUE
INNER JOIN tenants t ON lt.tenant_id = t.tenant_id
-- SELF JOIN to leases table
LEFT JOIN leases pred ON l.predecessor_lease_id = pred.lease_id
WHERE l.status IN ('ACTIVE', 'EXPIRING');
