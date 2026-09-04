from app.core.database import get_db_cursor
from app.core.exceptions import NotFoundError
from typing import List, Optional

class UnitService:
    @staticmethod
    def list_units(
        property_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        with get_db_cursor() as cur:
            query = """
                SELECT 
                    u.unit_id, u.building_id, b.name AS building_name, b.property_id,
                    p.name AS property_name, u.unit_number, u.unit_type,
                    u.status, u.floor_number, u.square_feet,
                    u.market_rent, u.is_active
                FROM units u
                JOIN buildings b ON u.building_id = b.building_id
                JOIN properties p ON b.property_id = p.property_id
                WHERE 1=1
            """
            params = []
            if property_id:
                query += " AND p.property_id = %s"
                params.append(property_id)
            if status:
                query += " AND u.status = %s"
                params.append(status)
            
            query += " ORDER BY u.unit_id ASC LIMIT %s OFFSET %s;"
            params.extend([limit, offset])
            cur.execute(query, tuple(params))
            return cur.fetchall()

    @staticmethod
    def get_unit(unit_id: int) -> dict:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    u.unit_id, u.building_id, b.name AS building_name, b.property_id,
                    p.name AS property_name, u.unit_number, u.unit_type,
                    u.status, u.floor_number, u.square_feet,
                    u.market_rent, u.is_active
                FROM units u
                JOIN buildings b ON u.building_id = b.building_id
                JOIN properties p ON b.property_id = p.property_id
                WHERE u.unit_id = %s;
            """, (unit_id,))
            unit = cur.fetchone()
            if not unit:
                raise NotFoundError(f"Unit {unit_id} not found")
            return unit
