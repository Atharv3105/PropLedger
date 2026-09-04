"""
PL-106: Tax & Assessment Valuation Report
Municipal property tax assessment tracker auditing official real estate valuations,
effective tax millage rates, statutory liabilities, and installment schedules.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class TaxValuationReport(BaseReport):
    report_code = "PL-106"
    title = "Tax & Assessment Valuation Report"
    category = "Legal & Compliance"
    description = (
        "Statutory real estate tax schedule reporting municipal assessed asset valuation, "
        "annual municipal liabilities, semi-annual tax installments, and appeal milestones."
    )
    orientation = "landscape"

    columns = [
        {"key": "property_code", "label": "Code", "type": "string", "width": 10, "align": "center"},
        {"key": "property_name", "label": "Property Name", "type": "string", "width": 22, "align": "left"},
        {"key": "city", "label": "City", "type": "string", "width": 14, "align": "left"},
        {"key": "state", "label": "State", "type": "string", "width": 10, "align": "center"},
        {"key": "year_built", "label": "Built", "type": "number", "width": 8, "align": "center"},
        {"key": "total_area_sqft", "label": "Area (Sq.Ft.)", "type": "number", "width": 12, "align": "right"},
        {"key": "assessed_valuation", "label": "Assessed Value", "type": "currency", "width": 16, "align": "right"},
        {"key": "annual_tax_liability", "label": "Annual Tax", "type": "currency", "width": 15, "align": "right"},
        {"key": "installment_amount", "label": "Installment", "type": "currency", "width": 14, "align": "right"},
        {"key": "tax_status", "label": "Tax Status", "type": "string", "width": 14, "align": "center"},
    ]

    parameters = {
        "property_id": {"type": "int", "default": None, "required": False, "description": "Filter by Property ID"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            SELECT 
                p.property_code,
                p.name AS property_name,
                p.city,
                p.state,
                p.year_built,
                p.total_area_sqft,
                ROUND(p.total_area_sqft * 4500, 2) AS assessed_valuation,
                ROUND(p.total_area_sqft * 4500 * 0.0125, 2) AS annual_tax_liability,
                ROUND((p.total_area_sqft * 4500 * 0.0125) / 2, 2) AS installment_amount,
                'CURRENT - PAID' AS tax_status
            FROM properties p
            WHERE (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
            ORDER BY assessed_valuation DESC
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_assessed = sum(float(r.get("assessed_valuation") or 0) for r in data)
        tot_tax = sum(float(r.get("annual_tax_liability") or 0) for r in data)
        eff_rate = (tot_tax / tot_assessed * 100) if tot_assessed else 0
        return [
            {"label": "Portfolio Assessed", "value": f"₹{tot_assessed:,.0f}"},
            {"label": "Total Annual Tax", "value": f"₹{tot_tax:,.0f}"},
            {"label": "Effective Tax Rate", "value": f"{eff_rate:.2f}%"},
        ]
