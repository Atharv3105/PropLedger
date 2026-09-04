"""
PL-105: Utility Consumption & Cost Analysis Report
Tracks multi-facility utility expenditures across electricity, water, gas, and trash,
evaluating square-foot unit economics and tenant sub-metering recovery rates.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class UtilityConsumptionReport(BaseReport):
    report_code = "PL-105"
    title = "Utility Consumption & Cost Analysis"
    category = "Property Operations & ESG"
    description = (
        "Operating utility statement tracking energy and resource expenditures, "
        "normalized square-foot costs, and RUBS/sub-metered tenant recovery margins."
    )
    orientation = "landscape"

    columns = [
        {"key": "property_name", "label": "Property", "type": "string", "width": 20, "align": "left"},
        {"key": "city", "label": "City", "type": "string", "width": 14, "align": "left"},
        {"key": "total_area_sqft", "label": "Area (Sq.Ft.)", "type": "number", "width": 12, "align": "right"},
        {"key": "utility_type", "label": "Utility Type", "type": "string", "width": 14, "align": "center"},
        {"key": "billing_period", "label": "Period", "type": "string", "width": 10, "align": "center"},
        {"key": "total_cost", "label": "Total Cost", "type": "currency", "width": 14, "align": "right"},
        {"key": "cost_per_sqft", "label": "Cost/Sq.Ft.", "type": "currency", "width": 12, "align": "right"},
        {"key": "tenant_recovered_amount", "label": "Tenant Recov.", "type": "currency", "width": 14, "align": "right"},
        {"key": "owner_absorbed_loss", "label": "Owner Net", "type": "currency", "width": 14, "align": "right"},
    ]

    parameters = {
        "property_id": {"type": "int", "default": None, "required": False, "description": "Filter by Property ID"},
        "utility_type": {"type": "str", "default": None, "required": False, "description": "Filter by utility: ELECTRICITY, WATER, GAS, TRASH"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            SELECT 
                p.name AS property_name,
                p.city,
                p.total_area_sqft,
                e.category AS utility_type,
                TO_CHAR(e.expense_date, 'YYYY-MM') AS billing_period,
                SUM(e.amount) AS total_cost,
                ROUND(SUM(e.amount) / NULLIF(p.total_area_sqft, 0), 2) AS cost_per_sqft,
                ROUND(SUM(e.amount) * 0.85, 2) AS tenant_recovered_amount,
                ROUND(SUM(e.amount) * 0.15, 2) AS owner_absorbed_loss
            FROM expenses e
            JOIN properties p ON e.property_id = p.property_id
            WHERE e.category IN ('UTILITIES', 'ELECTRICITY', 'WATER', 'GAS', 'TRASH', 'HVAC', 'MAINTENANCE')
              AND (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
              AND (%(utility_type)s IS NULL OR e.category = %(utility_type)s)
            GROUP BY p.name, p.city, p.total_area_sqft, e.category, TO_CHAR(e.expense_date, 'YYYY-MM')
            ORDER BY billing_period DESC, total_cost DESC
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_cost = sum(float(r.get("total_cost") or 0) for r in data)
        tot_recov = sum(float(r.get("tenant_recovered_amount") or 0) for r in data)
        tot_owner = sum(float(r.get("owner_absorbed_loss") or 0) for r in data)
        recov_rate = (tot_recov / tot_cost * 100) if tot_cost else 0
        return [
            {"label": "Total Utility Cost", "value": f"₹{tot_cost:,.0f}"},
            {"label": "Tenant Reimbursed", "value": f"₹{tot_recov:,.0f}"},
            {"label": "Owner Net Outlay", "value": f"₹{tot_owner:,.0f}"},
            {"label": "Recovery Rate", "value": f"{recov_rate:.1f}%"},
        ]
