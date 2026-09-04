from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.maintenance import MaintenanceRequestResponse, MaintenanceReopenRequest, MaintenanceReopenResponse
from app.services.maintenance_service import MaintenanceService
from app.core.rbac import require_roles

router = APIRouter(prefix="/maintenance", tags=["Maintenance"])

@router.get("", response_model=List[MaintenanceRequestResponse])
def list_maintenance_requests(
    status: Optional[str] = None,
    property_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "MAINTENANCE_STAFF", "TENANT"))
):
    return MaintenanceService.list_requests(status=status, property_id=property_id, limit=limit, offset=offset)

@router.post("/{request_id}/reopen", response_model=MaintenanceReopenResponse)
def reopen_maintenance_request(
    request_id: int,
    reopen_in: MaintenanceReopenRequest,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER"))
):
    return MaintenanceService.reopen_request(
        request_id=request_id,
        reason=reopen_in.reopen_reason,
        user_id=current_user["user_id"]
    )
