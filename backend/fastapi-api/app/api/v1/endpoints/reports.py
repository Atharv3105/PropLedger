from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from app.schemas.property import PropertyOccupancyStats
from app.schemas.collection import DelinquencyItem
from app.schemas.finance import FinancialSummaryResponse
from app.schemas.report import HierarchyNodeResponse, RentPivotResponse
from app.services.report_service import ReportService
from app.services.collection_service import CollectionService
from app.services.finance_service import FinanceService
from app.core.rbac import require_roles

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/occupancy", response_model=List[PropertyOccupancyStats])
def get_occupancy_report(
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "OWNER"))
):
    return ReportService.get_occupancy_report()

@router.get("/delinquency", response_model=List[DelinquencyItem])
def get_delinquency_report(
    property_id: Optional[int] = Query(None),
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT"))
):
    return CollectionService.get_delinquency_report(property_id=property_id)

@router.get("/financial-summary", response_model=List[FinancialSummaryResponse])
def get_financial_summary_report(
    property_id: Optional[int] = Query(None),
    current_user: dict = Depends(require_roles("ADMIN", "ACCOUNTANT", "OWNER"))
):
    return FinanceService.get_financial_summaries(property_id=property_id)

@router.get("/hierarchy", response_model=List[HierarchyNodeResponse])
def get_asset_hierarchy(
    max_level: int = Query(4, ge=1, le=10),
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER"))
):
    return ReportService.get_asset_hierarchy(max_level=max_level)

@router.get("/rent-pivot", response_model=List[RentPivotResponse])
def get_monthly_rent_pivot(
    limit: int = Query(50, ge=1, le=500),
    current_user: dict = Depends(require_roles("ADMIN", "ACCOUNTANT"))
):
    return ReportService.get_monthly_rent_pivot(limit=limit)
