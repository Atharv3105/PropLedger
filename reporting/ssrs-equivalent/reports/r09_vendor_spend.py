"""
PL-103: Vendor Spend & Performance Analysis Report
Procurement analysis tracking vendor disbursements across maintenance categories,
work order volumes, average billing sizes, and tax reporting / 1099 compliance.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class VendorSpendReport(BaseReport):
    report_code = "PL-103"
    title = "Vendor Spend & Performance Analysis"
    category = "Procurement & Vendors"
    description = (
        "Vendor procurement summary tracking invoice aggregate spend, trade classification, "
        "job count fulfillment, and mandatory tax reporting classification."
    )
    orientation = "landscape"

    columns = [
        {"key": "vendor_name", "label": "Vendor Company", "type": "string", "width": 22, "align": "left"},
        {"key": "trade_category", "label": "Trade Category", "type": "string", "width": 16, "align": "left"},
        {"key": "tax_id", "label": "Tax ID / PAN", "type": "string", "width": 14, "align": "center"},
        {"key": "phone", "label": "Contact Phone", "type": "string", "width": 14, "align": "center"},
        {"key": "total_invoices", "label": "Invoices", "type": "number", "width": 10, "align": "right"},
        {"key": "total_spend", "label": "Total Spend", "type": "currency", "width": 16, "align": "right"},
        {"key": "avg_invoice_amount", "label": "Avg Invoice", "type": "currency", "width": 14, "align": "right"},
        {"key": "work_orders_count", "label": "Work Orders", "type": "number", "width": 10, "align": "right"},
        {"key": "tax_reporting_status", "label": "1099 / Tax Status", "type": "string", "width": 16, "align": "center"},
    ]

    parameters = {
        "trade_category": {"type": "str", "default": None, "required": False, "description": "Filter by trade category"},
        "min_spend": {"type": "float", "default": 0.0, "required": False, "description": "Minimum spend threshold"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            SELECT 
                v.company_name AS vendor_name,
                v.trade_category,
                v.tax_id,
                v.phone,
                COUNT(DISTINCT e.expense_id) AS total_invoices,
                COALESCE(SUM(e.amount), 0) AS total_spend,
                ROUND(COALESCE(AVG(e.amount), 0), 2) AS avg_invoice_amount,
                COUNT(DISTINCT wo.work_order_id) AS work_orders_count,
                CASE WHEN COALESCE(SUM(e.amount), 0) >= 50000 THEN '1099-REQUIRED' ELSE 'EXEMPT' END AS tax_reporting_status
            FROM vendors v
            LEFT JOIN expenses e ON v.vendor_id = e.vendor_id
            LEFT JOIN work_orders wo ON v.vendor_id = wo.vendor_id
            WHERE (%(trade_category)s IS NULL OR v.trade_category = %(trade_category)s)
            GROUP BY v.company_name, v.trade_category, v.tax_id, v.phone
            HAVING COALESCE(SUM(e.amount), 0) >= %(min_spend)s
            ORDER BY total_spend DESC
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_spend = sum(float(r.get("total_spend") or 0) for r in data)
        req_1099 = sum(1 for r in data if r.get("tax_reporting_status") == "1099-REQUIRED")
        return [
            {"label": "Active Vendors", "value": f"{len(data):,}"},
            {"label": "Disbursed Capital", "value": f"₹{tot_spend:,.0f}"},
            {"label": "1099 Mandatory", "value": f"{req_1099:,}"},
        ]
