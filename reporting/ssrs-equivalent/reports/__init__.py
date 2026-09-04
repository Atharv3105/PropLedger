"""
PropLedger SSRS-Equivalent Report Catalog.
Exports all 14 standard institutional report definitions (PL-095 through PL-108).
"""
try:
    from .r01_rent_roll import RentRollReport
    from .r02_tenant_aging import TenantAgingReport
    from .r03_cash_flow import CashFlowReport
    from .r04_maintenance_work_order import MaintenanceWorkOrderReport
    from .r05_financial_pnl import PropertyFinancialPnlReport
    from .r06_lease_expiration import LeaseExpirationReport
    from .r07_capex_tracking import CapexTrackingReport
    from .r08_tenant_ledger import TenantLedgerReport
    from .r09_vendor_spend import VendorSpendReport
    from .r10_unit_turnover import UnitTurnoverReport
    from .r11_utility_consumption import UtilityConsumptionReport
    from .r12_tax_valuation import TaxValuationReport
    from .r13_insurance_claims import InsuranceClaimsReport
    from .r14_executive_dashboard import ExecutiveDashboardReport
except ImportError:
    from reports.r01_rent_roll import RentRollReport
    from reports.r02_tenant_aging import TenantAgingReport
    from reports.r03_cash_flow import CashFlowReport
    from reports.r04_maintenance_work_order import MaintenanceWorkOrderReport
    from reports.r05_financial_pnl import PropertyFinancialPnlReport
    from reports.r06_lease_expiration import LeaseExpirationReport
    from reports.r07_capex_tracking import CapexTrackingReport
    from reports.r08_tenant_ledger import TenantLedgerReport
    from reports.r09_vendor_spend import VendorSpendReport
    from reports.r10_unit_turnover import UnitTurnoverReport
    from reports.r11_utility_consumption import UtilityConsumptionReport
    from reports.r12_tax_valuation import TaxValuationReport
    from reports.r13_insurance_claims import InsuranceClaimsReport
    from reports.r14_executive_dashboard import ExecutiveDashboardReport

REPORT_CLASSES = [
    RentRollReport,
    TenantAgingReport,
    CashFlowReport,
    MaintenanceWorkOrderReport,
    PropertyFinancialPnlReport,
    LeaseExpirationReport,
    CapexTrackingReport,
    TenantLedgerReport,
    VendorSpendReport,
    UnitTurnoverReport,
    UtilityConsumptionReport,
    TaxValuationReport,
    InsuranceClaimsReport,
    ExecutiveDashboardReport,
]

__all__ = [
    "REPORT_CLASSES",
    "RentRollReport",
    "TenantAgingReport",
    "CashFlowReport",
    "MaintenanceWorkOrderReport",
    "PropertyFinancialPnlReport",
    "LeaseExpirationReport",
    "CapexTrackingReport",
    "TenantLedgerReport",
    "VendorSpendReport",
    "UnitTurnoverReport",
    "UtilityConsumptionReport",
    "TaxValuationReport",
    "InsuranceClaimsReport",
    "ExecutiveDashboardReport",
]
