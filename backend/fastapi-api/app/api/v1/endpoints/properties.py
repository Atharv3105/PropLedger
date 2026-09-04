from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.property import PropertyResponse, PropertyCreate, PropertyOccupancyStats
from app.services.property_service import PropertyService
from app.core.rbac import require_roles

router = APIRouter(prefix="/properties", tags=["Properties"])

@router.get("", response_model=List[PropertyResponse])
def list_properties(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT", "OWNER"))
):
    return PropertyService.list_properties(limit=limit, offset=offset, search=search)

@router.get("/{property_id}", response_model=PropertyResponse)
def get_property(
    property_id: int,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT", "OWNER"))
):
    return PropertyService.get_property(property_id)

@router.post("", response_model=PropertyResponse, status_code=201)
def create_property(
    property_in: PropertyCreate,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER"))
):
    return PropertyService.create_property(property_in.model_dump(), created_by=current_user["user_id"])

@router.get("/{property_id}/occupancy", response_model=PropertyOccupancyStats)
def get_property_occupancy(
    property_id: int,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "OWNER"))
):
    return PropertyService.get_property_occupancy(property_id)
