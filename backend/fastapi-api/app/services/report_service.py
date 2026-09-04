from app.core.database import get_db_cursor
from typing import List

class ReportService:
    @staticmethod
    def get_occupancy_report() -> List[dict]:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    property_id, property_code, property_name,
                    SUM(total_units) AS total_units,
                    SUM(occupied_units) AS occupied_units,
                    SUM(available_units) AS vacant_units,
                    SUM(maintenance_units) AS under_maintenance_units,
                    ROUND(AVG(occupancy_percentage), 2) AS occupancy_rate_pct
                FROM vw_PropertyOccupancy
                GROUP BY property_id, property_code, property_name
                ORDER BY occupancy_rate_pct DESC;
            """)
            return cur.fetchall()

    @staticmethod
    def get_asset_hierarchy(max_level: int = 4) -> List[dict]:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT node_id, parent_node_id, node_name, node_type, depth_level, hierarchy_path
                FROM vw_AssetHierarchyCTE
                WHERE depth_level <= %s
                ORDER BY hierarchy_path ASC
                LIMIT 100;
            """, (max_level,))
            return cur.fetchall()

    @staticmethod
    def get_monthly_rent_pivot(limit: int = 50) -> List[dict]:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    property_id, property_code, property_name, billing_year,
                    jan_collected, feb_collected, mar_collected, apr_collected,
                    may_collected, jun_collected, jul_collected, aug_collected,
                    sep_collected, oct_collected, nov_collected, dec_collected,
                    annual_total_collected
                FROM vw_MonthlyRentCollectionPivot
                ORDER BY property_id ASC
                LIMIT %s;
            """, (limit,))
            return cur.fetchall()
