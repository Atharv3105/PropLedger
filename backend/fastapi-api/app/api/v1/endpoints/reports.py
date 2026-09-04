import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, Request, Response
from app.schemas.property import PropertyOccupancyStats
from app.schemas.collection import DelinquencyItem
from app.schemas.finance import FinancialSummaryResponse
from app.schemas.report import HierarchyNodeResponse, RentPivotResponse
from app.services.report_service import ReportService
from app.services.collection_service import CollectionService
from app.services.finance_service import FinanceService
from app.core.rbac import require_roles

# Add SSRS reporting equivalent directory to sys.path
SSRS_DIR = Path(__file__).resolve().parents[6] / "reporting" / "ssrs-equivalent"
if str(SSRS_DIR) not in sys.path:
    sys.path.insert(0, str(SSRS_DIR))

# Add Crystal reporting equivalent directory to sys.path
CRYSTAL_DIR = Path(__file__).resolve().parents[6] / "reporting" / "crystal-equivalent"
if str(CRYSTAL_DIR) not in sys.path:
    sys.path.insert(0, str(CRYSTAL_DIR))

try:
    from registry import ReportRegistry
except ImportError:
    ReportRegistry = None

try:
    from statement_registry import StatementRegistry
except ImportError:
    StatementRegistry = None


router = APIRouter(prefix="/reports", tags=["Reports"])


# --------------------------------------------------------------------------
# Existing Phase 4 JSON Reporting Endpoints
# --------------------------------------------------------------------------

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


# --------------------------------------------------------------------------
# Phase 7 Crystal Reports-Equivalent Formal Statements Endpoints (PL-114 - PL-117)
# --------------------------------------------------------------------------

@router.get("/statements/catalog")
def get_statement_catalog(
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT", "OWNER"))
):
    """Returns catalog of institutional formal statement definitions (CR-01, CR-02, CR-03)."""
    if not StatementRegistry:
        raise HTTPException(status_code=500, detail="Statement engine unavailable")
    return StatementRegistry.list_statements()


@router.get("/statements/{statement_code}/pdf")
def export_statement_pdf(
    statement_code: str,
    request: Request,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT", "OWNER"))
):
    """Generates and streams formal section-banded statement PDF."""
    if not StatementRegistry:
        raise HTTPException(status_code=500, detail="Statement engine unavailable")
    stmt = StatementRegistry.get_statement(statement_code)
    if not stmt:
        raise HTTPException(status_code=404, detail=f"Statement '{statement_code}' not found in catalog")

    params = dict(request.query_params)
    pdf_bytes = stmt.export_pdf(params)

    filename = f"{stmt.statement_code.lower()}_{stmt.title.lower().replace(' ', '_')[:25]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/statements/tenant/{tenant_id}/statement")
def get_tenant_billing_statement_pdf(
    tenant_id: int,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT", "TENANT"))
):
    """Generates personal tenant statement of account with detachable remittance advice."""
    if not StatementRegistry:
        raise HTTPException(status_code=500, detail="Statement engine unavailable")
    stmt = StatementRegistry.get_statement("CR-01")
    if not stmt:
        raise HTTPException(status_code=404, detail="Tenant statement definition not found")

    pdf_bytes = stmt.export_pdf({"tenant_id": tenant_id})
    filename = f"stmt_tenant_{tenant_id}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


# --------------------------------------------------------------------------
# Phase 6 SSRS-Equivalent Enterprise Reporting Endpoints (PL-095 - PL-113)
# --------------------------------------------------------------------------

@router.get("/catalog")
def get_report_catalog(
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT", "OWNER"))
):
    """Returns catalog of all 14 standard institutional reports with schemas and parameters."""
    if not ReportRegistry:
        raise HTTPException(status_code=500, detail="Reporting engine unavailable")
    return ReportRegistry.list_reports()


@router.get("/{report_code}/data")
def get_report_data(
    report_code: str,
    request: Request,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT", "OWNER"))
):
    """Executes specified report and returns JSON data and summary KPI metrics."""
    if not ReportRegistry:
        raise HTTPException(status_code=500, detail="Reporting engine unavailable")
    report = ReportRegistry.get_report(report_code)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report '{report_code}' not found in catalog")

    params = dict(request.query_params)
    data = report.fetch_data(params)
    kpis = report.get_summary_stats(data)
    return {
        "report_code": report.report_code,
        "title": report.title,
        "category": report.category,
        "row_count": len(data),
        "kpis": kpis,
        "data": data,
    }


@router.get("/{report_code}/export/excel")
def export_report_excel(
    report_code: str,
    request: Request,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT", "OWNER"))
):
    """Generates and streams a publication-grade Excel workbook (.xlsx)."""
    if not ReportRegistry:
        raise HTTPException(status_code=500, detail="Reporting engine unavailable")
    report = ReportRegistry.get_report(report_code)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report '{report_code}' not found in catalog")

    params = dict(request.query_params)
    excel_bytes = report.export_excel(params)

    filename = f"{report.report_code.lower()}_{report.title.lower().replace(' ', '_')[:25]}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/{report_code}/export/pdf")
def export_report_pdf(
    report_code: str,
    request: Request,
    current_user: dict = Depends(require_roles("ADMIN", "PROPERTY_MANAGER", "ACCOUNTANT", "OWNER"))
):
    """Generates and streams a publication-grade paginated PDF report (.pdf)."""
    if not ReportRegistry:
        raise HTTPException(status_code=500, detail="Reporting engine unavailable")
    report = ReportRegistry.get_report(report_code)
    if not report:
        raise HTTPException(status_code=404, detail=f"Report '{report_code}' not found in catalog")

    params = dict(request.query_params)
    pdf_bytes = report.export_pdf(params)

    filename = f"{report.report_code.lower()}_{report.title.lower().replace(' ', '_')[:25]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )
