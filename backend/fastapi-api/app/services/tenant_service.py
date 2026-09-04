from app.core.database import get_db_cursor
from app.core.exceptions import NotFoundError
from typing import List, Optional

class TenantService:
    @staticmethod
    def list_tenants(limit: int = 50, offset: int = 0, search: Optional[str] = None) -> List[dict]:
        with get_db_cursor() as cur:
            query = """
                SELECT 
                    t.tenant_id, t.first_name, t.last_name,
                    (t.first_name || ' ' || t.last_name) AS full_name,
                    t.email, t.phone, t.credit_score, t.is_active
                FROM tenants t
            """
            params = []
            if search:
                query += " WHERE t.first_name ILIKE %s OR t.last_name ILIKE %s OR t.email ILIKE %s"
                pattern = f"%{search}%"
                params.extend([pattern, pattern, pattern])
            
            query += " ORDER BY t.tenant_id ASC LIMIT %s OFFSET %s;"
            params.extend([limit, offset])
            cur.execute(query, tuple(params))
            return cur.fetchall()

    @staticmethod
    def get_tenant_balance(tenant_id: int) -> dict:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    tenant_id, tenant_name, tenant_email, tenant_phone,
                    lease_id, property_name, unit_number, lease_status,
                    total_billed, total_paid, total_late_fees, outstanding_balance
                FROM vw_TenantOutstandingBalance
                WHERE tenant_id = %s
                LIMIT 1;
            """, (tenant_id,))
            bal = cur.fetchone()
            if not bal:
                raise NotFoundError(f"Tenant {tenant_id} not found in balance view")
            return bal
