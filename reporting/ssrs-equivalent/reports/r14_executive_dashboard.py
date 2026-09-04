"""
PL-108: Portfolio Executive Dashboard Summary Report
C-suite briefing report synthesizing cross-portfolio asset performance,
physical occupancy, annualized rent roll, net operating income, and asset cap rate.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class ExecutiveDashboardReport(BaseReport):
    report_code = "PL-108"
    title = "Portfolio Executive Dashboard Summary"
    category = "Executive Management & Board"
    description = (
        "Executive KPI briefing providing institutional oversight of asset density, "
        "portfolio-wide physical occupancy, gross annualized revenue, NOI, and cap rates."
    )
    orientation = "landscape"

    columns = [
        {"key": "property_name", "label": "Asset Name", "type": "string", "width": 22, "align": "left"},
        {"key": "city", "label": "Market / City", "type": "string", "width": 14, "align": "left"},
        {"key": "buildings_count", "label": "Bldgs", "type": "number", "width": 8, "align": "center"},
        {"key": "total_units", "label": "Total Units", "type": "number", "width": 10, "align": "right"},
        {"key": "occupied_units", "label": "Occupied", "type": "number", "width": 10, "align": "right"},
        {"key": "occupancy_pct", "label": "Occupancy", "type": "percent", "width": 12, "align": "right"},
        {"key": "monthly_contracted_rent", "label": "Monthly Rent", "type": "currency", "width": 15, "align": "right"},
        {"key": "annualized_gross_revenue", "label": "Annual Revenue", "type": "currency", "width": 16, "align": "right"},
        {"key": "net_operating_income", "label": "Estimated NOI", "type": "currency", "width": 16, "align": "right"},
        {"key": "cap_rate_pct", "label": "Cap Rate", "type": "percent", "width": 11, "align": "right"},
    ]

    parameters = {
        "portfolio_code": {"type": "str", "default": None, "required": False, "description": "Filter by Portfolio Code"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            SELECT 
                p.name AS property_name,
                p.city,
                COUNT(DISTINCT b.building_id) AS buildings_count,
                COUNT(DISTINCT u.unit_id) AS total_units,
                COUNT(DISTINCT CASE WHEN u.status = 'OCCUPIED' THEN u.unit_id END) AS occupied_units,
                ROUND(
                    (COUNT(DISTINCT CASE WHEN u.status = 'OCCUPIED' THEN u.unit_id END)::numeric / 
                    NULLIF(COUNT(DISTINCT u.unit_id), 0)) * 100, 1
                ) AS occupancy_pct,
                COALESCE(SUM(l.monthly_rent), 0) AS monthly_contracted_rent,
                COALESCE(SUM(l.monthly_rent) * 12, 0) AS annualized_gross_revenue,
                ROUND(COALESCE(SUM(l.monthly_rent) * 12 * 0.72, 0), 2) AS net_operating_income,
                ROUND(
                    (COALESCE(SUM(l.monthly_rent) * 12 * 0.72, 0) / 
                    NULLIF(p.total_area_sqft * 4500, 0)) * 100, 2
                ) AS cap_rate_pct
            FROM properties p
            JOIN buildings b ON p.property_id = b.property_id
            JOIN units u ON b.building_id = u.building_id
            LEFT JOIN leases l ON u.unit_id = l.unit_id AND l.status = 'ACTIVE'
            GROUP BY p.property_id, p.name, p.city, p.total_area_sqft
            ORDER BY annualized_gross_revenue DESC
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_props = len(data)
        tot_units = sum(int(r.get("total_units") or 0) for r in data)
        tot_occ = sum(int(r.get("occupied_units") or 0) for r in data)
        tot_ann = sum(float(r.get("annualized_gross_revenue") or 0) for r in data)
        tot_noi = sum(float(r.get("net_operating_income") or 0) for r in data)
        occ_rate = (tot_occ / tot_units * 100) if tot_units else 0
        return [
            {"label": "Portfolio Properties", "value": f"{tot_props:,}"},
            {"label": "Total Units", "value": f"{tot_units:,}"},
            {"label": "Portfolio Occupancy", "value": f"{occ_rate:.1f}%"},
            {"label": "Annualized Gross", "value": f"₹{tot_ann:,.0f}"},
            {"label": "Aggregate NOI", "value": f"₹{tot_noi:,.0f}"},
        ]
