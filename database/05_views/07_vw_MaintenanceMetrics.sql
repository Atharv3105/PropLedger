-- ======================================================================
-- View: vw_MaintenanceMetrics
-- Description: Aggregates maintenance resolution times, costs, and request counts
-- PRD Reference: Part I (Module 7), Part P (Report 9)
-- Techniques: Date arithmetic, EXTRACT, Conditional counting
-- ======================================================================

CREATE OR REPLACE VIEW vw_MaintenanceMetrics AS
SELECT 
    p.property_id,
    p.name AS property_name,
    mr.category,
    COUNT(mr.request_id) AS total_requests,
    SUM(CASE WHEN mr.status = 'OPEN' THEN 1 ELSE 0 END) AS open_requests,
    SUM(CASE WHEN mr.status = 'IN_PROGRESS' THEN 1 ELSE 0 END) AS in_progress_requests,
    SUM(CASE WHEN mr.status IN ('RESOLVED', 'CLOSED') THEN 1 ELSE 0 END) AS closed_requests,
    ROUND(
        AVG(
            CASE 
                WHEN mr.resolved_date IS NOT NULL THEN 
                    EXTRACT(EPOCH FROM (mr.resolved_date - mr.reported_date)) / 86400.0
                ELSE NULL 
            END
        )::NUMERIC, 1
    ) AS avg_resolution_days,
    COALESCE(SUM(wo.actual_cost), 0.00) AS total_maintenance_cost
FROM properties p
INNER JOIN buildings b ON p.property_id = b.property_id
INNER JOIN units u ON b.building_id = u.building_id
INNER JOIN maintenance_requests mr ON u.unit_id = mr.unit_id
LEFT JOIN work_orders wo ON mr.request_id = wo.request_id
GROUP BY p.property_id, p.name, mr.category;
