from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.tenant import TenantResponse, TenantBalanceResponse
from app.services.tenant_service import TenantService
from app.core.rbac import require_roles

router = APIRouter(prefix="/tenants", tags=["Tenants"])

@router.get("", response_model=List[TenantResponse])
def list_tenants(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "LEASING_STAFF", "ACCOUNTANT"))
):
    return TenantService.list_tenants(limit=limit, offset=offset, search=search)

@router.get("/{tenant_id}/balance", response_model=TenantBalanceResponse)
def get_tenant_balance(
    tenant_id: int,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT", "TENANT"))
):
    return TenantService.get_tenant_balance(tenant_id)
