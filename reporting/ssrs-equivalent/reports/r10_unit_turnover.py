"""
PL-104: Unit Turnover Cost & Downtime Report
Quantifies lost rent revenue and make-ready preparation expenses during
unit turnover downtime between consecutive lease occupancies.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class UnitTurnoverReport(BaseReport):
    report_code = "PL-104"
    title = "Unit Turnover Cost & Downtime"
    category = "Asset Management"
    description = (
        "Turnover operational review analyzing vacant days between occupancies, make-ready "
        "remediation outlays, forgone rent during turn, and aggregate turnover drag."
    )
    orientation = "landscape"

    columns = [
        {"key": "property_name", "label": "Property", "type": "string", "width": 20, "align": "left"},
        {"key": "unit_number", "label": "Unit", "type": "string", "width": 8, "align": "center"},
        {"key": "unit_type", "label": "Type", "type": "string", "width": 12, "align": "center"},
        {"key": "market_rent", "label": "Market Rent", "type": "currency", "width": 13, "align": "right"},
        {"key": "turnover_scope", "label": "Turnover Scope", "type": "string", "width": 16, "align": "left"},
        {"key": "turnover_prep_cost", "label": "Make-Ready Cost", "type": "currency", "width": 14, "align": "right"},
        {"key": "days_vacant", "label": "Vacant Days", "type": "number", "width": 10, "align": "right"},
        {"key": "lost_rent", "label": "Lost Rent", "type": "currency", "width": 13, "align": "right"},
        {"key": "total_turnover_cost", "label": "Total Turn Cost", "type": "currency", "width": 15, "align": "right"},
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
                u.unit_number,
                u.unit_type,
                u.market_rent,
                COALESCE(mr.category, 'Turnover Refresh') AS turnover_scope,
                COALESCE(wo.actual_cost, 4500.00) AS turnover_prep_cost,
                COALESCE(wo.completed_date - wo.scheduled_date, 14) AS days_vacant,
                ROUND((u.market_rent / 30.0) * COALESCE(wo.completed_date - wo.scheduled_date, 14), 2) AS lost_rent,
                ROUND(COALESCE(wo.actual_cost, 4500.00) + (u.market_rent / 30.0) * COALESCE(wo.completed_date - wo.scheduled_date, 14), 2) AS total_turnover_cost
            FROM units u
            JOIN buildings b ON u.building_id = b.building_id
            JOIN properties p ON b.property_id = p.property_id
            LEFT JOIN maintenance_requests mr ON u.unit_id = mr.unit_id
            LEFT JOIN work_orders wo ON mr.request_id = wo.request_id
            WHERE (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
              AND u.status IN ('AVAILABLE', 'UNDER_MAINTENANCE')
            ORDER BY total_turnover_cost DESC
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_prep = sum(float(r.get("turnover_prep_cost") or 0) for r in data)
        tot_lost = sum(float(r.get("lost_rent") or 0) for r in data)
        tot_cost = sum(float(r.get("total_turnover_cost") or 0) for r in data)
        vacant_days = [float(r.get("days_vacant") or 0) for r in data]
        avg_vacant = sum(vacant_days) / len(vacant_days) if vacant_days else 0
        return [
            {"label": "Units in Turn", "value": f"{len(data):,}"},
            {"label": "Make-Ready Outlay", "value": f"₹{tot_prep:,.0f}"},
            {"label": "Forgone Rent", "value": f"₹{tot_lost:,.0f}"},
            {"label": "Total Turnover Burden", "value": f"₹{tot_cost:,.0f}"},
            {"label": "Average Downtime", "value": f"{avg_vacant:.1f} Days"},
        ]
