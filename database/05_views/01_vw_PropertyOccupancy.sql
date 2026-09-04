-- ======================================================================
-- View: vw_PropertyOccupancy
-- Description: Aggregates occupancy metrics and percentage by property and building
-- PRD Reference: Part J, Part P (Report 1)
-- Techniques: Conditional Aggregation, Multi-table JOIN
-- ======================================================================

CREATE OR REPLACE VIEW vw_PropertyOccupancy AS
SELECT 
    p.property_id,
    p.property_code,
    p.name AS property_name,
    p.property_type,
    p.city,
    b.building_id,
    b.building_code,
    b.name AS building_name,
    COUNT(u.unit_id) AS total_units,
    SUM(CASE WHEN u.status = 'OCCUPIED' THEN 1 ELSE 0 END) AS occupied_units,
    SUM(CASE WHEN u.status = 'AVAILABLE' THEN 1 ELSE 0 END) AS available_units,
    SUM(CASE WHEN u.status = 'MAINTENANCE' THEN 1 ELSE 0 END) AS maintenance_units,
    SUM(CASE WHEN u.status = 'RESERVED' THEN 1 ELSE 0 END) AS reserved_units,
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
GROUP BY p.property_id, p.property_code, p.name, p.property_type, p.city, b.building_id, b.building_code, b.name;
