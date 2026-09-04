-- Query 1: Property Occupancy & Unit Status Portfolio Aggregation
-- Requirements: PL-132
-- Analyzes physical & economic occupancy across all properties and buildings
SELECT 
    p.property_id,
    p.name AS property_name,
    p.property_type,
    COUNT(u.unit_id) AS total_units,
    COUNT(CASE WHEN u.status = 'Occupied' THEN 1 END) AS occupied_units,
    COUNT(CASE WHEN u.status = 'Vacant' THEN 1 END) AS vacant_units,
    ROUND(COUNT(CASE WHEN u.status = 'Occupied' THEN 1 END)::numeric / NULLIF(COUNT(u.unit_id), 0) * 100, 2) AS occupancy_rate,
    COALESCE(SUM(u.market_rent), 0.00) AS gross_potential_rent,
    COALESCE(SUM(l.monthly_rent), 0.00) AS actual_contract_rent,
    ROUND(COALESCE(SUM(l.monthly_rent), 0.00) / NULLIF(SUM(u.market_rent), 0) * 100, 2) AS economic_occupancy_rate,
    COALESCE(SUM(u.square_feet), 0) AS total_sqft
FROM properties p
JOIN buildings b ON b.property_id = p.property_id
JOIN units u ON u.building_id = b.building_id
LEFT JOIN leases l ON l.unit_id = u.unit_id 
    AND l.status = 'Active' 
    AND l.start_date <= CURRENT_DATE 
    AND (l.end_date IS NULL OR l.end_date >= CURRENT_DATE)
GROUP BY p.property_id, p.name, p.property_type
ORDER BY occupancy_rate ASC, total_units DESC;
