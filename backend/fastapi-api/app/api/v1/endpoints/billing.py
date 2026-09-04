from fastapi import APIRouter, Depends
from app.schemas.billing import GenerateRentRequest, GenerateRentResponse
from app.services.billing_service import BillingService
from app.core.rbac import require_roles

router = APIRouter(prefix="/billing", tags=["Billing"])

@router.post("/generate-monthly", response_model=GenerateRentResponse)
def generate_monthly_rent(
    billing_in: GenerateRentRequest,
    current_user: dict = Depends(require_roles("ADMIN", "ACCOUNTANT"))
):
    return BillingService.generate_monthly_rent(
        billing_month=billing_in.billing_month,
        billing_year=billing_in.billing_year
    )
