-- ======================================================================
-- Procedure: usp_GetDelinquencyReport
-- Description: Categorizes overdue accounts into aging buckets with late fee assessment
-- PRD Reference: Part J (Conditional Aggregation), Part P (Report 6), Module 6
-- Techniques: Aging Buckets (Current, 1-30, 31-60, 61-90, 90+ days)
-- ======================================================================

CREATE OR REPLACE FUNCTION usp_GetDelinquencyReport(
    p_property_id BIGINT DEFAULT NULL,
    p_as_of_date DATE DEFAULT CURRENT_DATE
) RETURNS TABLE (
    tenant_id BIGINT,
    tenant_name TEXT,
    phone VARCHAR(50),
    property_name VARCHAR(150),
    unit_number VARCHAR(50),
    lease_id BIGINT,
    oldest_overdue_date DATE,
    days_overdue INT,
    total_unpaid_rent NUMERIC(12, 2),
    assessed_late_fee NUMERIC(10, 2),
    total_amount_due NUMERIC(14, 2),
    aging_category TEXT,
    collection_status VARCHAR(50)
) AS $$
BEGIN
    RETURN QUERY
    WITH OverdueCharges AS (
        SELECT 
            rc.lease_id,
            MIN(rc.due_date) AS oldest_overdue,
            (p_as_of_date - MIN(rc.due_date))::INT AS overdue_days,
            SUM(rc.charge_amount - rc.amount_paid) AS unpaid_rent
        FROM rent_charges rc
        WHERE rc.due_date < p_as_of_date 
          AND rc.status != 'PAID'
        GROUP BY rc.lease_id
        HAVING SUM(rc.charge_amount - rc.amount_paid) > 0
    )
    SELECT 
        t.tenant_id,
        (t.first_name || ' ' || t.last_name)::TEXT AS tenant_name,
        t.phone,
        p.name AS property_name,
        u.unit_number,
        l.lease_id,
        oc.oldest_overdue,
        oc.overdue_days,
        oc.unpaid_rent,
        fn_CalculateLateFee(l.lease_id, oc.unpaid_rent, oc.overdue_days) AS assessed_late_fee,
        (oc.unpaid_rent + fn_CalculateLateFee(l.lease_id, oc.unpaid_rent, oc.overdue_days)) AS total_amount_due,
        CASE 
            WHEN oc.overdue_days <= 30 THEN '1-30 Days'
            WHEN oc.overdue_days <= 60 THEN '31-60 Days'
            WHEN oc.overdue_days <= 90 THEN '61-90 Days'
            ELSE '90+ Days (Severe)'
        END AS aging_category,
        COALESCE(cc.status, 'PENDING_ACTION') AS collection_status
    FROM OverdueCharges oc
    INNER JOIN leases l ON oc.lease_id = l.lease_id
    INNER JOIN units u ON l.unit_id = u.unit_id
    INNER JOIN buildings b ON u.building_id = b.building_id
    INNER JOIN properties p ON b.property_id = p.property_id
    INNER JOIN lease_tenants lt ON l.lease_id = lt.lease_id AND lt.is_primary = TRUE
    INNER JOIN tenants t ON lt.tenant_id = t.tenant_id
    LEFT JOIN collection_cases cc ON l.lease_id = cc.lease_id AND cc.status != 'RESOLVED'
    WHERE (p_property_id IS NULL OR p.property_id = p_property_id)
    ORDER BY oc.overdue_days DESC, oc.unpaid_rent DESC;
END;
$$ LANGUAGE plpgsql STABLE;
