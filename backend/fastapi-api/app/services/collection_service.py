from app.core.database import get_db_cursor
from app.core.exceptions import BusinessRuleViolationError
from typing import List, Optional
import json

class CollectionService:
    @staticmethod
    def get_delinquency_report(property_id: Optional[int] = None) -> List[dict]:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    tenant_id, tenant_name, phone, property_name,
                    unit_number, lease_id, oldest_overdue_date,
                    days_overdue AS max_overdue_days,
                    total_unpaid_rent AS total_delinquent_balance,
                    assessed_late_fee, total_amount_due, aging_category,
                    collection_status
                FROM usp_GetDelinquencyReport(%s, CURRENT_DATE);
            """, (property_id,))
            rows = cur.fetchall()
            # Map aging buckets for API schema
            results = []
            for r in rows:
                amt = float(r["total_delinquent_balance"])
                days = r["max_overdue_days"]
                results.append({
                    "tenant_id": r["tenant_id"],
                    "tenant_name": r["tenant_name"],
                    "email": None,
                    "phone": r["phone"],
                    "lease_id": r["lease_id"],
                    "unit_number": r["unit_number"],
                    "property_name": r["property_name"],
                    "current_0_30": amt if days <= 30 else 0.0,
                    "past_due_31_60": amt if 30 < days <= 60 else 0.0,
                    "past_due_61_90": amt if 60 < days <= 90 else 0.0,
                    "severe_90_plus": amt if days > 90 else 0.0,
                    "total_delinquent_balance": amt,
                    "max_overdue_days": days
                })
            return results

    @staticmethod
    def escalate_to_collection(lease_id: int, user_id: int, notes: str) -> dict:
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                SELECT usp_EscalateToCollection(%s, %s, %s) AS result;
            """, (lease_id, user_id, notes))
            row = cur.fetchone()
            result = row["result"] if isinstance(row["result"], dict) else json.loads(row["result"])
            return {
                "collection_case_id": result.get("case_id", 0),
                "tenant_id": result.get("tenant_id", 0),
                "lease_id": lease_id,
                "delinquent_amount": float(result.get("overdue_amount", 0.0)),
                "status": result.get("status", "OPEN"),
                "message": result.get("message", "Lease escalated to formal collections")
            }
