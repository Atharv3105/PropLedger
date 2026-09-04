from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.finance import ExpenseResponse, FinancialSummaryResponse
from app.services.finance_service import FinanceService
from app.core.rbac import require_roles

router = APIRouter(prefix="/finance", tags=["Finance"])

@router.get("/expenses", response_model=List[ExpenseResponse])
def list_expenses(
    property_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT"))
):
    return FinanceService.list_expenses(property_id=property_id, limit=limit, offset=offset)

@router.get("/financial-summary", response_model=List[FinancialSummaryResponse])
def get_financial_summary(
    property_id: Optional[int] = None,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT"))
):
    return FinanceService.get_financial_summaries(property_id=property_id)
