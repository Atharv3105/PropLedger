from fastapi import APIRouter, Depends, Query
from typing import List
from app.schemas.lease import ActiveLeaseResponse, LeaseRenewRequest, LeaseRenewResponse
from app.services.lease_service import LeaseService
from app.core.rbac import require_roles

router = APIRouter(prefix="/leases", tags=["Leases"])

@router.get("/active", response_model=List[ActiveLeaseResponse])
def list_active_leases(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "LEASING_STAFF"))
):
    return LeaseService.list_active_leases(limit=limit, offset=offset)

@router.post("/{lease_id}/renew", response_model=LeaseRenewResponse)
def renew_lease(
    lease_id: int,
    renew_in: LeaseRenewRequest,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "LEASING_STAFF"))
):
    return LeaseService.renew_lease(
        predecessor_lease_id=lease_id,
        new_start_date=renew_in.new_start_date,
        new_end_date=renew_in.new_end_date,
        new_monthly_rent=renew_in.new_monthly_rent,
        user_id=current_user["user_id"]
    )
