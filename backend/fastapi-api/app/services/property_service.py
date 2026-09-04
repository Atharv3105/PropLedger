from app.core.database import get_db_cursor
from app.core.exceptions import NotFoundError
from typing import List, Optional

class PropertyService:
    @staticmethod
    def list_properties(limit: int = 50, offset: int = 0, search: Optional[str] = None) -> List[dict]:
        with get_db_cursor() as cur:
            query = """
                SELECT 
                    p.property_id, p.property_code, p.name AS property_name, p.property_type,
                    p.address_line1, p.city, p.state, p.postal_code,
                    p.year_built, p.total_area_sqft,
                    COUNT(DISTINCT b.building_id) AS total_buildings,
                    COUNT(DISTINCT u.unit_id) AS total_units
                FROM properties p
                LEFT JOIN buildings b ON p.property_id = b.property_id
                LEFT JOIN units u ON b.building_id = u.building_id
            """
            params = []
            if search:
                query += " WHERE p.name ILIKE %s OR p.property_code ILIKE %s OR p.city ILIKE %s"
                pattern = f"%{search}%"
                params.extend([pattern, pattern, pattern])
            
            query += """
                GROUP BY p.property_id
                ORDER BY p.property_id ASC
                LIMIT %s OFFSET %s;
            """
            params.extend([limit, offset])
            cur.execute(query, tuple(params))
            return cur.fetchall()

    @staticmethod
    def get_property(property_id: int) -> dict:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    p.property_id, p.property_code, p.name AS property_name, p.property_type,
                    p.address_line1, p.city, p.state, p.postal_code,
                    p.year_built, p.total_area_sqft,
                    COUNT(DISTINCT b.building_id) AS total_buildings,
                    COUNT(DISTINCT u.unit_id) AS total_units
                FROM properties p
                LEFT JOIN buildings b ON p.property_id = b.property_id
                LEFT JOIN units u ON b.building_id = u.building_id
                WHERE p.property_id = %s
                GROUP BY p.property_id;
            """, (property_id,))
            prop = cur.fetchone()
            if not prop:
                raise NotFoundError(f"Property with ID {property_id} not found")
            return prop

    @staticmethod
    def create_property(data: dict, created_by: int) -> dict:
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                INSERT INTO properties (
                    property_code, name, property_type, address_line1,
                    city, state, postal_code, year_built, total_area_sqft,
                    created_by
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING property_id, property_code, name AS property_name, property_type,
                          address_line1, city, state, postal_code,
                          year_built, total_area_sqft,
                          0 AS total_buildings, 0 AS total_units;
            """, (
                data["property_code"], data["property_name"], data.get("property_type", "COMMERCIAL"),
                data["address_line1"], data["city"], data["state"],
                data["postal_code"], data.get("year_built"),
                data.get("total_area_sqft"), created_by
            ))
            return cur.fetchone()

    @staticmethod
    def get_property_occupancy(property_id: int) -> dict:
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
                WHERE property_id = %s
                GROUP BY property_id, property_code, property_name;
            """, (property_id,))
            occ = cur.fetchone()
            if not occ:
                raise NotFoundError(f"Occupancy metrics not found for Property {property_id}")
            return occ
