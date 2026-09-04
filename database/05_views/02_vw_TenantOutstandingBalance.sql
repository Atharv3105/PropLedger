-- ======================================================================
-- View: vw_TenantOutstandingBalance
-- Description: Computes real-time running financial balance per tenant and lease
-- PRD Reference: Part J, Module 5
-- Techniques: LEFT JOIN, COALESCE, Subquery Aggregation
-- ======================================================================

CREATE OR REPLACE VIEW vw_TenantOutstandingBalance AS
SELECT 
    t.tenant_id,
    t.first_name || ' ' || t.last_name AS tenant_name,
    t.email AS tenant_email,
    t.phone AS tenant_phone,
    l.lease_id,
    p.name AS property_name,
    u.unit_number,
    l.status AS lease_status,
    COALESCE(charges.total_billed, 0.00) AS total_billed,
    COALESCE(payments.total_paid, 0.00) AS total_paid,
    COALESCE(fees.total_fees, 0.00) AS total_late_fees,
    ROUND((COALESCE(charges.total_billed, 0.00) + COALESCE(fees.total_fees, 0.00) - COALESCE(payments.total_paid, 0.00)), 2) AS outstanding_balance
FROM tenants t
INNER JOIN lease_tenants lt ON t.tenant_id = lt.tenant_id AND lt.is_primary = TRUE
INNER JOIN leases l ON lt.lease_id = l.lease_id
INNER JOIN units u ON l.unit_id = u.unit_id
INNER JOIN buildings b ON u.building_id = b.building_id
INNER JOIN properties p ON b.property_id = p.property_id
LEFT JOIN (
    SELECT lease_id, SUM(charge_amount) AS total_billed
    FROM rent_charges
    GROUP BY lease_id
) charges ON l.lease_id = charges.lease_id
LEFT JOIN (
    SELECT lease_id, SUM(amount) AS total_paid
    FROM payments
    GROUP BY lease_id
) payments ON l.lease_id = payments.lease_id
LEFT JOIN (
    SELECT rc.lease_id, SUM(lf.fee_amount) AS total_fees
    FROM late_fees lf
    INNER JOIN rent_charges rc ON lf.charge_id = rc.charge_id
    WHERE lf.is_waived = FALSE
    GROUP BY rc.lease_id
) fees ON l.lease_id = fees.lease_id;
