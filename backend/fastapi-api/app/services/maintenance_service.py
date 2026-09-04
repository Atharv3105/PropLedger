from app.core.database import get_db_cursor
from app.core.exceptions import BusinessRuleViolationError
import json
from typing import List, Optional

class MaintenanceService:
    @staticmethod
    def list_requests(
        status: Optional[str] = None,
        property_id: Optional[int] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[dict]:
        with get_db_cursor() as cur:
            query = """
                SELECT 
                    mr.request_id, ('MRQ-' || mr.request_id::TEXT) AS request_number,
                    mr.unit_id, u.unit_number, p.name AS property_name,
                    mr.category, mr.priority, mr.status,
                    mr.description, mr.reported_date
                FROM maintenance_requests mr
                JOIN units u ON mr.unit_id = u.unit_id
                JOIN buildings b ON u.building_id = b.building_id
                JOIN properties p ON b.property_id = p.property_id
                WHERE 1=1
            """
            params = []
            if status:
                query += " AND mr.status ILIKE %s"
                params.append(status)
            if property_id:
                query += " AND p.property_id = %s"
                params.append(property_id)
            
            query += " ORDER BY mr.reported_date DESC LIMIT %s OFFSET %s;"
            params.extend([limit, offset])
            cur.execute(query, tuple(params))
            return cur.fetchall()

    @staticmethod
    def reopen_request(request_id: int, reason: str, user_id: int) -> dict:
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                SELECT usp_ReopenMaintenanceRequest(%s, %s, %s) AS result;
            """, (request_id, reason, user_id))
            row = cur.fetchone()
            result = row["result"] if isinstance(row["result"], dict) else json.loads(row["result"])
            
            if result.get("status") == "NOT_MODIFIED":
                raise BusinessRuleViolationError(result.get("message", "Cannot reopen ticket"), "BR-08")
                
            return {
                "request_id": request_id,
                "request_number": f"MRQ-{request_id}",
                "new_status": result.get("new_status", "OPEN"),
                "message": f"Maintenance request #{request_id} successfully reopened with audit trail"
            }
