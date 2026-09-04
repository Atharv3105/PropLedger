"""
PL-100: Lease Expiration Schedule Report
Lease expiration schedule tracking leases expiring within 30, 60, 90, 180, and 365 days,
projecting tenant retention, rent roll rollover risk, and lease renewal status.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class LeaseExpirationReport(BaseReport):
    report_code = "PL-100"
    title = "Lease Expiration Schedule"
    category = "Operations & Leasing"
    description = (
        "Forward-looking lease maturity schedule quantifying renewal exposure, "
        "days remaining on active agreements, contracted rent, and retention pipeline."
    )
    orientation = "landscape"

    columns = [
        {"key": "property_name", "label": "Property", "type": "string", "width": 20, "align": "left"},
        {"key": "unit_number", "label": "Unit", "type": "string", "width": 8, "align": "center"},
        {"key": "primary_tenant_name", "label": "Tenant Name", "type": "string", "width": 20, "align": "left"},
        {"key": "primary_tenant_phone", "label": "Phone", "type": "string", "width": 14, "align": "center"},
        {"key": "start_date", "label": "Start Date", "type": "date", "width": 11, "align": "center"},
        {"key": "end_date", "label": "End Date", "type": "date", "width": 11, "align": "center"},
        {"key": "days_remaining", "label": "Days Left", "type": "number", "width": 10, "align": "right"},
        {"key": "monthly_rent", "label": "Rent at Risk", "type": "currency", "width": 14, "align": "right"},
        {"key": "renewal_status", "label": "Renewal Status", "type": "string", "width": 14, "align": "center"},
        {"key": "lease_status", "label": "Status", "type": "string", "width": 10, "align": "center"},
    ]

    parameters = {
        "property_id": {"type": "int", "default": None, "required": False, "description": "Filter by Property ID"},
        "horizon_days": {"type": "int", "default": 365, "required": False, "description": "Maturity horizon in days"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            SELECT 
                property_name,
                unit_number,
                primary_tenant_name,
                primary_tenant_phone,
                start_date,
                end_date,
                days_remaining,
                monthly_rent,
                COALESCE(renewal_status, 'PENDING') AS renewal_status,
                lease_status
            FROM vw_activeleases
            WHERE (%(property_id)s IS NULL OR property_id = %(property_id)s)
              AND days_remaining <= %(horizon_days)s
            ORDER BY days_remaining ASC
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_expiring = len(data)
        tot_rent = sum(float(r.get("monthly_rent") or 0) for r in data)
        renewed = sum(1 for r in data if r.get("renewal_status") in ("RENEWED", "COMPLETED"))
        retention = (renewed / tot_expiring * 100) if tot_expiring else 0
        return [
            {"label": "Expiring Leases", "value": f"{tot_expiring:,}"},
            {"label": "Monthly Rent at Risk", "value": f"₹{tot_rent:,.0f}"},
            {"label": "Renewals Secured", "value": f"{renewed:,}"},
            {"label": "Retention Rate", "value": f"{retention:.1f}%"},
        ]
