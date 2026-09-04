"""
PL-097: Cash Flow Statement Report
Comprehensive statement tracking monthly operating inflows (rent collections,
late fees) against operating outflows (vendor payments, repairs) and net cash flow.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class CashFlowReport(BaseReport):
    report_code = "PL-097"
    title = "Cash Flow Statement"
    category = "Financial Management"
    description = (
        "Operating cash flow statement showing realized monthly inflows, operational "
        "outflows, net cash flow, and operating expense ratio (OER)."
    )
    orientation = "landscape"

    columns = [
        {"key": "property_name", "label": "Property", "type": "string", "width": 24, "align": "left"},
        {"key": "period", "label": "Period", "type": "string", "width": 12, "align": "center"},
        {"key": "operating_inflow", "label": "Operating Inflows", "type": "currency", "width": 18, "align": "right"},
        {"key": "operating_outflow", "label": "Operating Outflows", "type": "currency", "width": 18, "align": "right"},
        {"key": "net_cash_flow", "label": "Net Cash Flow", "type": "currency", "width": 18, "align": "right"},
        {"key": "expense_ratio_pct", "label": "OER (%)", "type": "percent", "width": 12, "align": "right"},
    ]

    parameters = {
        "property_id": {"type": "int", "default": None, "required": False, "description": "Filter by Property ID"},
        "year": {"type": "int", "default": None, "required": False, "description": "Filter by Calendar Year (e.g. 2024)"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            WITH monthly_inflows AS (
                SELECT 
                    p.property_id,
                    p.name AS property_name,
                    TO_CHAR(pay.payment_date, 'YYYY-MM') AS month_year,
                    SUM(pay.amount) AS total_inflow
                FROM payments pay
                JOIN leases l ON pay.lease_id = l.lease_id
                JOIN units u ON l.unit_id = u.unit_id
                JOIN buildings b ON u.building_id = b.building_id
                JOIN properties p ON b.property_id = p.property_id
                WHERE (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
                  AND (%(year)s IS NULL OR EXTRACT(YEAR FROM pay.payment_date) = %(year)s)
                GROUP BY p.property_id, p.name, TO_CHAR(pay.payment_date, 'YYYY-MM')
            ),
            monthly_outflows AS (
                SELECT 
                    p.property_id,
                    p.name AS property_name,
                    TO_CHAR(e.expense_date, 'YYYY-MM') AS month_year,
                    SUM(e.amount) AS total_outflow
                FROM expenses e
                JOIN properties p ON e.property_id = p.property_id
                WHERE (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
                  AND (%(year)s IS NULL OR EXTRACT(YEAR FROM e.expense_date) = %(year)s)
                GROUP BY p.property_id, p.name, TO_CHAR(e.expense_date, 'YYYY-MM')
            )
            SELECT 
                COALESCE(i.property_name, o.property_name) AS property_name,
                COALESCE(i.month_year, o.month_year) AS period,
                COALESCE(i.total_inflow, 0) AS operating_inflow,
                COALESCE(o.total_outflow, 0) AS operating_outflow,
                (COALESCE(i.total_inflow, 0) - COALESCE(o.total_outflow, 0)) AS net_cash_flow,
                ROUND(
                    CASE WHEN COALESCE(i.total_inflow, 0) > 0 
                         THEN (COALESCE(o.total_outflow, 0) / i.total_inflow) * 100 
                         ELSE 0 END, 1
                ) AS expense_ratio_pct
            FROM monthly_inflows i
            FULL OUTER JOIN monthly_outflows o 
              ON i.property_id = o.property_id AND i.month_year = o.month_year
            ORDER BY period DESC, property_name
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_in = sum(float(r.get("operating_inflow") or 0) for r in data)
        tot_out = sum(float(r.get("operating_outflow") or 0) for r in data)
        net_cf = tot_in - tot_out
        avg_oer = (tot_out / tot_in * 100) if tot_in else 0
        return [
            {"label": "Total Inflows", "value": f"₹{tot_in:,.0f}"},
            {"label": "Total Outflows", "value": f"₹{tot_out:,.0f}"},
            {"label": "Net Operating Cash Flow", "value": f"₹{net_cf:,.0f}"},
            {"label": "Average OER", "value": f"{avg_oer:.1f}%"},
        ]
