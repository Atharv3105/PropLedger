from app.core.database import get_db_cursor
from app.core.exceptions import BusinessRuleViolationError
import json
from typing import List, Optional

class PaymentService:
    @staticmethod
    def record_payment(
        lease_id: int,
        amount: float,
        payment_method: str = "BANK_TRANSFER",
        reference_number: Optional[str] = None,
        recorded_by: int = 1
    ) -> dict:
        if amount <= 0:
            raise BusinessRuleViolationError("Payment amount must be strictly positive per Rule BR-10", "BR-10")
            
        ref_no = reference_number or f"PAY-{lease_id}-AUTO"
        with get_db_cursor(commit=True) as cur:
            cur.execute("""
                SELECT usp_RecordPayment(%s, %s, %s, %s, %s) AS result;
            """, (lease_id, amount, payment_method, ref_no, recorded_by))
            row = cur.fetchone()
            result = row["result"] if isinstance(row["result"], dict) else json.loads(row["result"])
            
            payment_id = result["payment_id"]
            
            # Query allocations count
            cur.execute("""
                SELECT COUNT(*) AS alloc_count, COALESCE(SUM(allocated_amount), 0) AS total_allocated
                FROM payment_allocations
                WHERE payment_id = %s;
            """, (payment_id,))
            alloc_stat = cur.fetchone()
            
            return {
                "payment_id": payment_id,
                "lease_id": lease_id,
                "amount_paid": float(result["amount"]),
                "allocated_amount": float(alloc_stat["total_allocated"]),
                "unallocated_amount": float(result["unallocated_credit"]),
                "remaining_balance": float(result["outstanding_balance"]),
                "allocations_count": alloc_stat["alloc_count"],
                "message": "Payment recorded and allocated via FIFO successfully"
            }

    @staticmethod
    def get_tenant_payment_history(tenant_id: int, lease_id: Optional[int] = None) -> List[dict]:
        with get_db_cursor() as cur:
            cur.execute("""
                SELECT 
                    payment_id, lease_id, payment_date, payment_method,
                    amount AS payment_amount, running_total_paid,
                    days_since_prior_payment AS days_since_last_payment,
                    row_num AS payment_rank
                FROM usp_GetTenantPaymentHistory(%s, %s);
            """, (tenant_id, lease_id))
            return cur.fetchall()
