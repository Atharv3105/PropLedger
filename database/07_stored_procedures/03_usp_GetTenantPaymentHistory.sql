-- ======================================================================
-- Procedure: usp_GetTenantPaymentHistory
-- Description: Returns payment transactions with Window Functions (LAG, ROW_NUMBER, Running Sum)
-- PRD Reference: Part J (Window Functions), Part P (Report 7)
-- Techniques: ROW_NUMBER(), LAG(), SUM() OVER()
-- ======================================================================

CREATE OR REPLACE FUNCTION usp_GetTenantPaymentHistory(
    p_tenant_id BIGINT DEFAULT NULL,
    p_lease_id BIGINT DEFAULT NULL
) RETURNS TABLE (
    row_num BIGINT,
    payment_id BIGINT,
    lease_id BIGINT,
    tenant_name TEXT,
    property_name VARCHAR(150),
    unit_number VARCHAR(50),
    payment_date DATE,
    amount NUMERIC(12, 2),
    payment_method VARCHAR(50),
    reference_number VARCHAR(100),
    days_since_prior_payment INT,
    running_total_paid NUMERIC(14, 2)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        ROW_NUMBER() OVER (PARTITION BY l.lease_id ORDER BY p.payment_date, p.payment_id) AS row_num,
        p.payment_id,
        l.lease_id,
        (t.first_name || ' ' || t.last_name)::TEXT AS tenant_name,
        prop.name AS property_name,
        u.unit_number,
        p.payment_date,
        p.amount,
        p.payment_method,
        p.reference_number,
        (p.payment_date - LAG(p.payment_date) OVER (PARTITION BY l.lease_id ORDER BY p.payment_date, p.payment_id))::INT AS days_since_prior_payment,
        SUM(p.amount) OVER (PARTITION BY l.lease_id ORDER BY p.payment_date, p.payment_id ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total_paid
    FROM payments p
    INNER JOIN leases l ON p.lease_id = l.lease_id
    INNER JOIN units u ON l.unit_id = u.unit_id
    INNER JOIN buildings b ON u.building_id = b.building_id
    INNER JOIN properties prop ON b.property_id = prop.property_id
    INNER JOIN lease_tenants lt ON l.lease_id = lt.lease_id AND lt.is_primary = TRUE
    INNER JOIN tenants t ON lt.tenant_id = t.tenant_id
    WHERE (p_tenant_id IS NULL OR t.tenant_id = p_tenant_id)
      AND (p_lease_id IS NULL OR l.lease_id = p_lease_id)
    ORDER BY l.lease_id, p.payment_date, p.payment_id;
END;
$$ LANGUAGE plpgsql STABLE;
