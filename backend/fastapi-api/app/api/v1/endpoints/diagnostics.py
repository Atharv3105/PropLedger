from fastapi import APIRouter, Depends
from app.schemas.diagnostics import HealthResponse, IncidentResponse
from app.services.diagnostics_service import DiagnosticsService
from app.core.rbac import require_roles

router = APIRouter(prefix="/diagnostics", tags=["Diagnostics"])

@router.get("/health", response_model=HealthResponse)
def health_check():
    return DiagnosticsService.get_system_health()

@router.get("/incidents", response_model=IncidentResponse)
def get_incidents(
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER"))
):
    return DiagnosticsService.get_recent_incidents()
