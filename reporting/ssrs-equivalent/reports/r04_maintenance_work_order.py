"""
PL-098: Maintenance Work Order Performance Report
Detailed operational tracking of work order throughput, turnaround time (MTTR),
vendor assignment, priority distribution, and budget vs actual costs.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class MaintenanceWorkOrderReport(BaseReport):
    report_code = "PL-098"
    title = "Maintenance Work Order Performance"
    category = "Operations & Maintenance"
    description = (
        "Operational efficiency audit tracking work order resolution timelines, "
        "priority distribution, vendor execution, and repair cost variance."
    )
    orientation = "landscape"

    columns = [
        {"key": "work_order_id", "label": "WO #", "type": "number", "width": 8, "align": "center"},
        {"key": "property_name", "label": "Property", "type": "string", "width": 18, "align": "left"},
        {"key": "unit_number", "label": "Unit", "type": "string", "width": 8, "align": "center"},
        {"key": "priority", "label": "Priority", "type": "string", "width": 10, "align": "center"},
        {"key": "category", "label": "Category", "type": "string", "width": 12, "align": "left"},
        {"key": "vendor_name", "label": "Assigned Vendor", "type": "string", "width": 18, "align": "left"},
        {"key": "scheduled_date", "label": "Scheduled", "type": "date", "width": 11, "align": "center"},
        {"key": "completed_date", "label": "Completed", "type": "date", "width": 11, "align": "center"},
        {"key": "turnaround_days", "label": "Days", "type": "number", "width": 8, "align": "right"},
        {"key": "estimated_cost", "label": "Est. Cost", "type": "currency", "width": 12, "align": "right"},
        {"key": "actual_cost", "label": "Act. Cost", "type": "currency", "width": 12, "align": "right"},
        {"key": "cost_variance", "label": "Variance", "type": "currency", "width": 12, "align": "right"},
        {"key": "status", "label": "Status", "type": "string", "width": 12, "align": "center"},
    ]

    parameters = {
        "property_id": {"type": "int", "default": None, "required": False, "description": "Filter by Property ID"},
        "priority": {"type": "str", "default": None, "required": False, "description": "Filter by Priority: EMERGENCY, HIGH, MEDIUM, LOW"},
        "status": {"type": "str", "default": None, "required": False, "description": "Filter by Status: COMPLETED, IN_PROGRESS, SCHEDULED"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            SELECT 
                wo.work_order_id,
                p.name AS property_name,
                u.unit_number,
                mr.priority,
                mr.category,
                COALESCE(v.company_name, wo.assigned_technician, 'Internal Tech') AS vendor_name,
                wo.scheduled_date,
                wo.completed_date,
                COALESCE(wo.completed_date - wo.scheduled_date, 0) AS turnaround_days,
                wo.estimated_cost,
                wo.actual_cost,
                (wo.actual_cost - wo.estimated_cost) AS cost_variance,
                wo.status
            FROM work_orders wo
            JOIN maintenance_requests mr ON wo.request_id = mr.request_id
            JOIN units u ON mr.unit_id = u.unit_id
            JOIN buildings b ON u.building_id = b.building_id
            JOIN properties p ON b.property_id = p.property_id
            LEFT JOIN vendors v ON wo.vendor_id = v.vendor_id
            WHERE (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
              AND (%(priority)s IS NULL OR mr.priority = %(priority)s)
              AND (%(status)s IS NULL OR wo.status = %(status)s)
            ORDER BY wo.work_order_id DESC
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        total_wos = len(data)
        completed = sum(1 for r in data if r.get("status") == "COMPLETED")
        tot_act_cost = sum(float(r.get("actual_cost") or 0) for r in data)
        days_list = [float(r.get("turnaround_days")) for r in data if r.get("turnaround_days") is not None and r.get("turnaround_days") >= 0]
        avg_days = sum(days_list) / len(days_list) if days_list else 0
        return [
            {"label": "Total Work Orders", "value": f"{total_wos:,}"},
            {"label": "Completed Count", "value": f"{completed:,}"},
            {"label": "Completion Rate", "value": f"{(completed/total_wos*100):.1f}%"},
            {"label": "Total Spend", "value": f"₹{tot_act_cost:,.0f}"},
            {"label": "Mean Resolution", "value": f"{avg_days:.1f} Days"},
        ]
