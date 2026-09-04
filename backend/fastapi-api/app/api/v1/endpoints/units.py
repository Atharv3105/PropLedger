from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.unit import UnitResponse
from app.services.unit_service import UnitService
from app.core.rbac import require_roles

router = APIRouter(prefix="/units", tags=["Units"])

@router.get("", response_model=List[UnitResponse])
def list_units(
    property_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "LEASING_STAFF", "TENANT"))
):
    return UnitService.list_units(property_id=property_id, status=status, limit=limit, offset=offset)

@router.get("/{unit_id}", response_model=UnitResponse)
def get_unit(
    unit_id: int,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "LEASING_STAFF"))
):
    return UnitService.get_unit(unit_id)
