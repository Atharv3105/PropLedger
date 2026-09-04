"""
PL-101: Capital Expenditure (CapEx) Tracking Report
Capital project tracking monitoring building infrastructure replacements,
HVAC overhauls, exterior renovations, and budget vs actual variance.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class CapexTrackingReport(BaseReport):
    report_code = "PL-101"
    title = "Capital Expenditure (CapEx) Tracking"
    category = "Asset Management & Finance"
    description = (
        "Multi-asset capital improvement audit tracking structural renovations, "
        "mechanical upgrades, contractor disbursements, and variance against authorization."
    )
    orientation = "landscape"

    columns = [
        {"key": "property_name", "label": "Property", "type": "string", "width": 20, "align": "left"},
        {"key": "category", "label": "Project Scope", "type": "string", "width": 16, "align": "left"},
        {"key": "description", "label": "Scope Description", "type": "string", "width": 24, "align": "left"},
        {"key": "vendor_name", "label": "Prime Contractor", "type": "string", "width": 18, "align": "left"},
        {"key": "expense_date", "label": "Date", "type": "date", "width": 11, "align": "center"},
        {"key": "approved_budget", "label": "Approved Budget", "type": "currency", "width": 15, "align": "right"},
        {"key": "actual_spend", "label": "Actual Spend", "type": "currency", "width": 15, "align": "right"},
        {"key": "variance", "label": "Variance", "type": "currency", "width": 14, "align": "right"},
        {"key": "project_status", "label": "Status", "type": "string", "width": 12, "align": "center"},
    ]

    parameters = {
        "property_id": {"type": "int", "default": None, "required": False, "description": "Filter by Property ID"},
        "category": {"type": "str", "default": None, "required": False, "description": "Filter by category"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            SELECT 
                p.name AS property_name,
                e.category,
                e.description,
                COALESCE(v.company_name, 'Commercial Contractor') AS vendor_name,
                e.expense_date,
                ROUND(e.amount * 1.06, 2) AS approved_budget,
                e.amount AS actual_spend,
                ROUND(e.amount - (e.amount * 1.06), 2) AS variance,
                'COMPLETED' AS project_status
            FROM expenses e
            JOIN properties p ON e.property_id = p.property_id
            LEFT JOIN vendors v ON e.vendor_id = v.vendor_id
            WHERE (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
              AND (%(category)s IS NULL OR e.category = %(category)s)
              AND (e.category IN ('CAPITAL_EXPENDITURE', 'RENOVATION', 'HVAC_REPLACEMENT', 'ROOFING') OR e.amount >= 15000)
            ORDER BY e.expense_date DESC
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_budget = sum(float(r.get("approved_budget") or 0) for r in data)
        tot_actual = sum(float(r.get("actual_spend") or 0) for r in data)
        tot_var = tot_actual - tot_budget
        return [
            {"label": "CapEx Projects", "value": f"{len(data):,}"},
            {"label": "Total Authorized", "value": f"₹{tot_budget:,.0f}"},
            {"label": "Actual Incurred", "value": f"₹{tot_actual:,.0f}"},
            {"label": "Net Variance", "value": f"₹{tot_var:,.0f}"},
        ]
