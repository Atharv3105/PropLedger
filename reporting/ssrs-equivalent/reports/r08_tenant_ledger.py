"""
PL-102: Tenant Payment History & Ledger Report
Itemized accounting statement for tenant accounts showing chronologically ordered
charges, payments, late fees, credit adjustments, and running account balance.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class TenantLedgerReport(BaseReport):
    report_code = "PL-102"
    title = "Tenant Payment History & Ledger"
    category = "Tenant Accounting"
    description = (
        "Double-entry chronological ledger detailing rent charges, receipts, "
        "concessions, and dynamic running balance for audit compliance."
    )
    orientation = "landscape"

    columns = [
        {"key": "property_name", "label": "Property", "type": "string", "width": 18, "align": "left"},
        {"key": "unit_number", "label": "Unit", "type": "string", "width": 8, "align": "center"},
        {"key": "tenant_name", "label": "Tenant Name", "type": "string", "width": 18, "align": "left"},
        {"key": "txn_date", "label": "Date", "type": "date", "width": 11, "align": "center"},
        {"key": "txn_type", "label": "Type", "type": "string", "width": 10, "align": "center"},
        {"key": "description", "label": "Description", "type": "string", "width": 24, "align": "left"},
        {"key": "debit_amount", "label": "Billed (Debit)", "type": "currency", "width": 14, "align": "right"},
        {"key": "credit_amount", "label": "Paid (Credit)", "type": "currency", "width": 14, "align": "right"},
        {"key": "running_balance", "label": "Balance", "type": "currency", "width": 14, "align": "right"},
    ]

    parameters = {
        "tenant_id": {"type": "int", "default": None, "required": False, "description": "Filter by Tenant ID"},
        "lease_id": {"type": "int", "default": None, "required": False, "description": "Filter by Lease ID"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            WITH raw_ledger AS (
                SELECT 
                    rc.lease_id,
                    rc.charge_date AS txn_date,
                    'CHARGE' AS txn_type,
                    'Monthly Rent Charge - ' || rc.billing_month || '/' || rc.billing_year AS description,
                    rc.charge_amount AS debit_amount,
                    0.00 AS credit_amount
                FROM rent_charges rc
                UNION ALL
                SELECT 
                    p.lease_id,
                    p.payment_date AS txn_date,
                    'PAYMENT' AS txn_type,
                    'Payment Received (' || p.payment_method || ')' AS description,
                    0.00 AS debit_amount,
                    p.amount AS credit_amount
                FROM payments p
            )
            SELECT 
                prop.name AS property_name,
                u.unit_number,
                t.first_name || ' ' || t.last_name AS tenant_name,
                rl.txn_date,
                rl.txn_type,
                rl.description,
                rl.debit_amount,
                rl.credit_amount,
                SUM(rl.debit_amount - rl.credit_amount) OVER (
                    PARTITION BY rl.lease_id 
                    ORDER BY rl.txn_date, rl.txn_type DESC
                ) AS running_balance
            FROM raw_ledger rl
            JOIN leases l ON rl.lease_id = l.lease_id
            JOIN units u ON l.unit_id = u.unit_id
            JOIN buildings b ON u.building_id = b.building_id
            JOIN properties prop ON b.property_id = prop.property_id
            JOIN lease_tenants lt ON l.lease_id = lt.lease_id AND lt.is_primary = TRUE
            JOIN tenants t ON lt.tenant_id = t.tenant_id
            WHERE (%(tenant_id)s IS NULL OR t.tenant_id = %(tenant_id)s)
              AND (%(lease_id)s IS NULL OR l.lease_id = %(lease_id)s)
            ORDER BY prop.name, u.unit_number, rl.txn_date
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        tot_debit = sum(float(r.get("debit_amount") or 0) for r in data)
        tot_credit = sum(float(r.get("credit_amount") or 0) for r in data)
        final_bal = tot_debit - tot_credit
        return [
            {"label": "Total Postings", "value": f"{len(data):,}"},
            {"label": "Total Debited", "value": f"₹{tot_debit:,.0f}"},
            {"label": "Total Credited", "value": f"₹{tot_credit:,.0f}"},
            {"label": "Net Outstanding", "value": f"₹{final_bal:,.0f}"},
        ]
