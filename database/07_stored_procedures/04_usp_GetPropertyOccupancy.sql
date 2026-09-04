-- ======================================================================
-- Procedure: usp_GetPropertyOccupancy
-- Description: Parameterized occupancy report with DENSE_RANK performance tiering
-- PRD Reference: Part J (Window Functions), Part P (Report 1)
-- Techniques: DENSE_RANK() OVER, Conditional Aggregation
-- ======================================================================

CREATE OR REPLACE FUNCTION usp_GetPropertyOccupancy(
    p_property_id BIGINT DEFAULT NULL
) RETURNS TABLE (
    occupancy_rank BIGINT,
    property_id BIGINT,
    property_code VARCHAR(50),
    property_name VARCHAR(150),
    property_type VARCHAR(50),
    city VARCHAR(100),
    total_units BIGINT,
    occupied_units BIGINT,
    available_units BIGINT,
    maintenance_units BIGINT,
    occupancy_percentage NUMERIC(5, 2)
) AS $$
BEGIN
    RETURN QUERY
    WITH PropertyStats AS (
        SELECT 
            p.property_id,
            p.property_code,
            p.name AS property_name,
            p.property_type,
            p.city,
            COUNT(u.unit_id) AS total_units,
            SUM(CASE WHEN u.status = 'OCCUPIED' THEN 1 ELSE 0 END) AS occupied_units,
            SUM(CASE WHEN u.status = 'AVAILABLE' THEN 1 ELSE 0 END) AS available_units,
            SUM(CASE WHEN u.status = 'MAINTENANCE' THEN 1 ELSE 0 END) AS maintenance_units,
            ROUND(
                CASE 
                    WHEN COUNT(u.unit_id) > 0 THEN 
                        (SUM(CASE WHEN u.status = 'OCCUPIED' THEN 1 ELSE 0 END)::NUMERIC / COUNT(u.unit_id)::NUMERIC) * 100.0
                    ELSE 0.0 
                END, 2
            ) AS occupancy_percentage
        FROM properties p
        INNER JOIN buildings b ON p.property_id = b.property_id
        LEFT JOIN units u ON b.building_id = u.building_id
        WHERE (p_property_id IS NULL OR p.property_id = p_property_id)
        GROUP BY p.property_id, p.property_code, p.name, p.property_type, p.city
    )
    SELECT 
        DENSE_RANK() OVER (ORDER BY ps.occupancy_percentage DESC, ps.total_units DESC) AS occupancy_rank,
        ps.property_id,
        ps.property_code,
        ps.property_name,
        ps.property_type,
        ps.city,
        ps.total_units,
        ps.occupied_units,
        ps.available_units,
        ps.maintenance_units,
        ps.occupancy_percentage
    FROM PropertyStats ps
    ORDER BY occupancy_rank, ps.property_name;
END;
$$ LANGUAGE plpgsql STABLE;
