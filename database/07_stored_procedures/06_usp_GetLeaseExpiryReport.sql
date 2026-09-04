-- ======================================================================
-- Procedure: usp_GetLeaseExpiryReport
-- Description: Identifies leases terminating within a parameterized date window
-- PRD Reference: Part J, Part P (Report 4), Module 4
-- ======================================================================

CREATE OR REPLACE FUNCTION usp_GetLeaseExpiryReport(
    p_from_date DATE,
    p_to_date DATE,
    p_property_id BIGINT DEFAULT NULL
) RETURNS TABLE (
    lease_id BIGINT,
    tenant_name TEXT,
    tenant_email VARCHAR(255),
    tenant_phone VARCHAR(50),
    property_name VARCHAR(150),
    unit_number VARCHAR(50),
    start_date DATE,
    end_date DATE,
    days_remaining INT,
    monthly_rent NUMERIC(12, 2),
    renewal_status VARCHAR(50),
    lease_status VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        l.lease_id,
        (t.first_name || ' ' || t.last_name)::TEXT AS tenant_name,
        t.email AS tenant_email,
        t.phone AS tenant_phone,
        p.name AS property_name,
        u.unit_number,
        l.start_date,
        l.end_date,
        (l.end_date - CURRENT_DATE)::INT AS days_remaining,
        l.monthly_rent,
        l.renewal_status,
        l.status AS lease_status
    FROM leases l
    INNER JOIN units u ON l.unit_id = u.unit_id
    INNER JOIN buildings b ON u.building_id = b.building_id
    INNER JOIN properties p ON b.property_id = p.property_id
    INNER JOIN lease_tenants lt ON l.lease_id = lt.lease_id AND lt.is_primary = TRUE
    INNER JOIN tenants t ON lt.tenant_id = t.tenant_id
    WHERE l.end_date BETWEEN p_from_date AND p_to_date
      AND (p_property_id IS NULL OR p.property_id = p_property_id)
      AND l.status != 'TERMINATED'
    ORDER BY l.end_date ASC;
END;
$$ LANGUAGE plpgsql STABLE;
