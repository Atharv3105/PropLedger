"""
PL-096: Tenant Aging & Delinquency Report
Aging bucket analysis of unpaid receivables categorized into 30, 60, 90,
and 90+ day arrears with tenant contact details and legal collection status.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class TenantAgingReport(BaseReport):
    report_code = "PL-096"
    title = "Tenant Aging & Delinquency Report"
    category = "Collections & Arrears"
    description = (
        "Delinquency aging schedule showing tenant outstanding balances categorized "
        "into 1-30, 31-60, 61-90, and >90 day buckets with direct contact channels."
    )
    orientation = "landscape"

    columns = [
        {"key": "tenant_name", "label": "Tenant Name", "type": "string", "width": 20, "align": "left"},
        {"key": "property_name", "label": "Property", "type": "string", "width": 18, "align": "left"},
        {"key": "unit_number", "label": "Unit", "type": "string", "width": 8, "align": "center"},
        {"key": "phone", "label": "Phone", "type": "string", "width": 14, "align": "center"},
        {"key": "bucket_1_30", "label": "1-30 Days", "type": "currency", "width": 13, "align": "right"},
        {"key": "bucket_31_60", "label": "31-60 Days", "type": "currency", "width": 13, "align": "right"},
        {"key": "bucket_61_90", "label": "61-90 Days", "type": "currency", "width": 13, "align": "right"},
        {"key": "bucket_90_plus", "label": ">90 Days", "type": "currency", "width": 13, "align": "right"},
        {"key": "total_overdue", "label": "Total Overdue", "type": "currency", "width": 15, "align": "right"},
        {"key": "collection_status", "label": "Collection Case", "type": "string", "width": 15, "align": "center"},
    ]

    parameters = {
        "property_id": {"type": "int", "default": None, "required": False, "description": "Filter by Property ID"},
        "min_overdue": {"type": "float", "default": 0.0, "required": False, "description": "Minimum overdue threshold"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            SELECT 
                t.first_name || ' ' || t.last_name AS tenant_name,
                p.name AS property_name,
                u.unit_number,
                t.phone,
                COALESCE(SUM(CASE WHEN CURRENT_DATE - rc.due_date BETWEEN 1 AND 30 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END), 0) AS bucket_1_30,
                COALESCE(SUM(CASE WHEN CURRENT_DATE - rc.due_date BETWEEN 31 AND 60 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END), 0) AS bucket_31_60,
                COALESCE(SUM(CASE WHEN CURRENT_DATE - rc.due_date BETWEEN 61 AND 90 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END), 0) AS bucket_61_90,
                COALESCE(SUM(CASE WHEN CURRENT_DATE - rc.due_date > 90 THEN (rc.charge_amount - rc.amount_paid) ELSE 0 END), 0) AS bucket_90_plus,
                COALESCE(SUM(rc.charge_amount - rc.amount_paid), 0) AS total_overdue,
                COALESCE(cc.status, 'CURRENT') AS collection_status
            FROM rent_charges rc
            JOIN leases l ON rc.lease_id = l.lease_id
            JOIN units u ON l.unit_id = u.unit_id
            JOIN buildings b ON u.building_id = b.building_id
            JOIN properties p ON b.property_id = p.property_id
            JOIN lease_tenants lt ON l.lease_id = lt.lease_id AND lt.is_primary = TRUE
            JOIN tenants t ON lt.tenant_id = t.tenant_id
            LEFT JOIN collection_cases cc ON l.lease_id = cc.lease_id AND cc.status = 'OPEN'
            WHERE rc.status IN ('PENDING', 'OVERDUE', 'PARTIALLY_PAID')
              AND rc.due_date < CURRENT_DATE
              AND (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
            GROUP BY p.name, u.unit_number, t.first_name, t.last_name, t.phone, cc.status
            HAVING SUM(rc.charge_amount - rc.amount_paid) >= %(min_overdue)s
            ORDER BY total_overdue DESC
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_overdue = sum(float(r.get("total_overdue") or 0) for r in data)
        b30 = sum(float(r.get("bucket_1_30") or 0) for r in data)
        b60 = sum(float(r.get("bucket_31_60") or 0) for r in data)
        b90 = sum(float(r.get("bucket_61_90") or 0) for r in data)
        b90p = sum(float(r.get("bucket_90_plus") or 0) for r in data)
        return [
            {"label": "Delinquent Accounts", "value": f"{len(data):,}"},
            {"label": "Total Delinquent", "value": f"₹{tot_overdue:,.0f}"},
            {"label": "1-30 Days Arrears", "value": f"₹{b30:,.0f}"},
            {"label": "31-60 Days Arrears", "value": f"₹{b60:,.0f}"},
            {"label": ">90 Days Arrears", "value": f"₹{b90p:,.0f}"},
        ]
