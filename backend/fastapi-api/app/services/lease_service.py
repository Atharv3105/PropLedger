from app.core.database import get_db_cursor
from app.core.exceptions import NotFoundError
import json
from typing import List

class LeaseService:
    @staticmethod
    def list_active_leases(limit: int = 50, offset: int = 0) -> List[dict]:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    lease_id, ('LSE-' || lease_id::TEXT) AS lease_number,
                    unit_id, unit_number, building_name, property_name,
                    tenant_id, primary_tenant_name, primary_tenant_email, primary_tenant_phone,
                    start_date, end_date, monthly_rent, security_deposit,
                    lease_status, predecessor_lease_id,
                    (predecessor_lease_id IS NOT NULL) AS is_renewal
                FROM vw_ActiveLeases
                ORDER BY lease_id ASC
                LIMIT %s OFFSET %s;
            """, (limit, offset))
            return cur.fetchall()

    @staticmethod
    def renew_lease(
        predecessor_lease_id: int,
        new_start_date,
        new_end_date,
        new_monthly_rent,
        user_id: int
    ) -> dict:
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                SELECT usp_RenewLease(%s, %s, %s, %s, %s) AS result;
            """, (predecessor_lease_id, new_start_date, new_end_date, new_monthly_rent, user_id))
            row = cur.fetchone()
            result = row["result"] if isinstance(row["result"], dict) else json.loads(row["result"])
            
            return {
                "new_lease_id": result["new_lease_id"],
                "lease_number": f"LSE-{result['new_lease_id']}",
                "predecessor_lease_id": result.get("old_lease_id", predecessor_lease_id),
                "message": f"Successfully renewed lease #{predecessor_lease_id} into new lease #{result['new_lease_id']}"
            }
