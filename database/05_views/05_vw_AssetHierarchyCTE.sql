-- ======================================================================
-- View: vw_AssetHierarchyCTE
-- Description: Recursive CTE demonstrating physical property asset hierarchy
-- PRD Reference: Part J (Ordinary & Recursive CTE demonstration)
-- Techniques: WITH RECURSIVE, Unified Adjacency, Path Tracking, Depth Tracking
-- ======================================================================

CREATE OR REPLACE VIEW vw_AssetHierarchyCTE AS
WITH RECURSIVE 
AllNodes AS (
    -- Level 1: Owners
    SELECT 
        'OWNER-' || owner_id::TEXT AS node_id, 
        NULL::TEXT AS parent_node_id, 
        contact_name AS node_name, 
        'OWNER' AS node_type 
    FROM owners
    
    UNION ALL
    
    -- Level 2: Properties
    SELECT 
        'PROP-' || property_id::TEXT, 
        'OWNER-' || owner_id::TEXT, 
        name, 
        'PROPERTY' 
    FROM properties
    
    UNION ALL
    
    -- Level 3: Buildings
    SELECT 
        'BLD-' || building_id::TEXT, 
        'PROP-' || property_id::TEXT, 
        name, 
        'BUILDING' 
    FROM buildings
    
    UNION ALL
    
    -- Level 4: Units
    SELECT 
        'UNIT-' || unit_id::TEXT, 
        'BLD-' || building_id::TEXT, 
        'Unit ' || unit_number, 
        'UNIT' 
    FROM units
),
AssetTree AS (
    -- Anchor Member: Root Nodes (Owners)
    SELECT 
        node_id, 
        parent_node_id, 
        node_name, 
        node_type, 
        1 AS depth_level, 
        ('/' || node_name)::TEXT AS hierarchy_path
    FROM AllNodes
    WHERE parent_node_id IS NULL

    UNION ALL

    -- Recursive Member: Traverse Children (Properties -> Buildings -> Units)
    SELECT 
        child.node_id,
        child.parent_node_id,
        child.node_name,
        child.node_type,
        parent.depth_level + 1,
        (parent.hierarchy_path || '/' || child.node_name)::TEXT
    FROM AllNodes child
    INNER JOIN AssetTree parent ON child.parent_node_id = parent.node_id
)
SELECT * FROM AssetTree;
