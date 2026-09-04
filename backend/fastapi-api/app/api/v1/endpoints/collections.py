from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.collection import DelinquencyItem, CollectionEscalateRequest, CollectionEscalateResponse
from app.services.collection_service import CollectionService
from app.core.rbac import require_roles

router = APIRouter(prefix="/collections", tags=["Collections"])

@router.get("/delinquent", response_model=List[DelinquencyItem])
def get_delinquency_report(
    property_id: Optional[int] = Query(None),
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT"))
):
    return CollectionService.get_delinquency_report(property_id=property_id)

@router.post("/escalate", response_model=CollectionEscalateResponse)
def escalate_to_collection(
    escalate_in: CollectionEscalateRequest,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT"))
):
    return CollectionService.escalate_to_collection(
        lease_id=escalate_in.lease_id,
        user_id=current_user["user_id"],
        notes=escalate_in.case_notes or "Escalated to collections via API"
    )
