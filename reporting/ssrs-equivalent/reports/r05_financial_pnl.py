"""
PL-099: Property Financial P&L Statement Report
Property-level Profit and Loss statement tracking Gross Operating Revenue,
Operating Expenses, Net Operating Income (NOI), Margin, and Physical Occupancy.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class PropertyFinancialPnlReport(BaseReport):
    report_code = "PL-099"
    title = "Property Financial P&L Statement"
    category = "Executive Financial"
    description = (
        "Consolidated property-by-property Profit & Loss statement reporting realized "
        "gross revenue, operating expenditure, net operating income, and NOI margin."
    )
    orientation = "landscape"

    columns = [
        {"key": "property_name", "label": "Property Name", "type": "string", "width": 24, "align": "left"},
        {"key": "property_type", "label": "Asset Type", "type": "string", "width": 14, "align": "center"},
        {"key": "city", "label": "City", "type": "string", "width": 14, "align": "left"},
        {"key": "gross_revenue", "label": "Gross Revenue", "type": "currency", "width": 18, "align": "right"},
        {"key": "operating_expenses", "label": "Operating Expenses", "type": "currency", "width": 18, "align": "right"},
        {"key": "net_operating_income", "label": "Net Operating Income", "type": "currency", "width": 18, "align": "right"},
        {"key": "noi_margin_pct", "label": "NOI Margin (%)", "type": "percent", "width": 14, "align": "right"},
        {"key": "occupancy_pct", "label": "Occupancy (%)", "type": "percent", "width": 14, "align": "right"},
    ]

    parameters = {
        "property_id": {"type": "int", "default": None, "required": False, "description": "Filter by Property ID"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            SELECT 
                p.name AS property_name,
                p.property_type,
                p.city,
                COALESCE(fs.total_operating_revenue, 0) AS gross_revenue,
                COALESCE(fs.total_operating_expenses, 0) AS operating_expenses,
                COALESCE(fs.net_operating_income, 0) AS net_operating_income,
                CASE WHEN COALESCE(fs.total_operating_revenue, 0) > 0 
                     THEN ROUND((fs.net_operating_income / fs.total_operating_revenue) * 100, 1) 
                     ELSE 0 END AS noi_margin_pct,
                COALESCE(occ.occupancy_percentage, 0) AS occupancy_pct
            FROM properties p
            LEFT JOIN (
                SELECT 
                    property_id,
                    SUM(total_operating_revenue) AS total_operating_revenue,
                    SUM(total_operating_expenses) AS total_operating_expenses,
                    SUM(net_operating_income) AS net_operating_income
                FROM vw_propertyfinancialsummary
                GROUP BY property_id
            ) fs ON p.property_id = fs.property_id
            LEFT JOIN (
                SELECT 
                    property_id,
                    ROUND(AVG(occupancy_percentage), 1) AS occupancy_percentage
                FROM vw_propertyoccupancy
                GROUP BY property_id
            ) occ ON p.property_id = occ.property_id
            WHERE (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
            ORDER BY net_operating_income DESC
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_rev = sum(float(r.get("gross_revenue") or 0) for r in data)
        tot_exp = sum(float(r.get("operating_expenses") or 0) for r in data)
        tot_noi = sum(float(r.get("net_operating_income") or 0) for r in data)
        avg_margin = (tot_noi / tot_rev * 100) if tot_rev else 0
        return [
            {"label": "Portfolio Revenue", "value": f"₹{tot_rev:,.0f}"},
            {"label": "Portfolio Expenses", "value": f"₹{tot_exp:,.0f}"},
            {"label": "Portfolio NOI", "value": f"₹{tot_noi:,.0f}"},
            {"label": "Aggregate NOI Margin", "value": f"{avg_margin:.1f}%"},
        ]
