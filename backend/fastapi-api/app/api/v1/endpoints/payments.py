from fastapi import APIRouter, Depends
from typing import List, Optional
from app.schemas.payment import PaymentCreateRequest, PaymentResponse, TenantPaymentHistoryItem
from app.services.payment_service import PaymentService
from app.core.rbac import require_roles

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("", response_model=PaymentResponse, status_code=201)
def record_payment(
    payment_in: PaymentCreateRequest,
    current_user: dict = Depends(require_roles("ADMIN", "ACCOUNTANT", "TENANT"))
):
    return PaymentService.record_payment(
        lease_id=payment_in.lease_id,
        amount=float(payment_in.amount),
        payment_method="BANK_TRANSFER" if payment_in.payment_method_id == 1 else "CREDIT_CARD",
        reference_number=payment_in.reference_number,
        recorded_by=current_user["user_id"]
    )

@router.get("/history/{tenant_id}", response_model=List[TenantPaymentHistoryItem])
def get_payment_history(
    tenant_id: int,
    lease_id: Optional[int] = None,
    current_user: dict = Depends(require_roles("ADMIN", "ACCOUNTANT", "TENANT"))
):
    return PaymentService.get_tenant_payment_history(tenant_id=tenant_id, lease_id=lease_id)
