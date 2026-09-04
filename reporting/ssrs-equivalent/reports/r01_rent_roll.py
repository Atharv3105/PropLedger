"""
PL-095: Rent Roll & Occupancy Summary Report
Asset-level rent roll listing each property, building, unit, tenant,
lease term, square footage, market rent, actual contracted rent,
variance, and occupancy status.
"""
from typing import Any, Dict, List, Optional
try:
    from engine.base_report import BaseReport
except ImportError:
    from ..engine.base_report import BaseReport


class RentRollReport(BaseReport):
    report_code = "PL-095"
    title = "Rent Roll & Occupancy Summary"
    category = "Operations & Leasing"
    description = (
        "Comprehensive property rent roll showing unit-by-unit tenancy, contracted "
        "vs market rent, square footage, lease expiration dates, and occupancy state."
    )
    orientation = "landscape"

    columns = [
        {"key": "property_name", "label": "Property", "type": "string", "width": 20, "align": "left"},
        {"key": "building_name", "label": "Building", "type": "string", "width": 16, "align": "left"},
        {"key": "unit_number", "label": "Unit", "type": "string", "width": 10, "align": "center"},
        {"key": "unit_type", "label": "Type", "type": "string", "width": 12, "align": "center"},
        {"key": "square_feet", "label": "Sq.Ft.", "type": "number", "width": 10, "align": "right"},
        {"key": "tenant_name", "label": "Tenant Name", "type": "string", "width": 22, "align": "left"},
        {"key": "market_rent", "label": "Market Rent", "type": "currency", "width": 14, "align": "right"},
        {"key": "contracted_rent", "label": "Contract Rent", "type": "currency", "width": 14, "align": "right"},
        {"key": "variance", "label": "Variance", "type": "currency", "width": 12, "align": "right"},
        {"key": "start_date", "label": "Lease Start", "type": "date", "width": 12, "align": "center"},
        {"key": "end_date", "label": "Lease End", "type": "date", "width": 12, "align": "center"},
        {"key": "occupancy_status", "label": "Status", "type": "string", "width": 14, "align": "center"},
    ]

    parameters = {
        "property_id": {"type": "int", "default": None, "required": False, "description": "Filter by Property ID"},
        "occupancy_status": {"type": "str", "default": None, "required": False, "description": "Filter by status: OCCUPIED, AVAILABLE, UNDER_MAINTENANCE"},
        "limit": {"type": "int", "default": 250, "required": False, "description": "Maximum records to return"},
    }

    def fetch_data(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        p = self.validate_params(params)
        query = """
            SELECT 
                p.name AS property_name,
                b.name AS building_name,
                u.unit_number,
                u.unit_type,
                u.square_feet,
                u.market_rent,
                COALESCE(l.monthly_rent, 0) AS contracted_rent,
                (u.market_rent - COALESCE(l.monthly_rent, 0)) AS variance,
                COALESCE(t.first_name || ' ' || t.last_name, 'VACANT') AS tenant_name,
                l.start_date,
                l.end_date,
                u.status AS occupancy_status
            FROM units u
            JOIN buildings b ON u.building_id = b.building_id
            JOIN properties p ON b.property_id = p.property_id
            LEFT JOIN leases l ON u.unit_id = l.unit_id AND l.status = 'ACTIVE'
            LEFT JOIN lease_tenants lt ON l.lease_id = lt.lease_id AND lt.is_primary = TRUE
            LEFT JOIN tenants t ON lt.tenant_id = t.tenant_id
            WHERE (%(property_id)s IS NULL OR p.property_id = %(property_id)s)
              AND (%(occupancy_status)s IS NULL OR %(occupancy_status)s = 'ALL' OR u.status = %(occupancy_status)s)
            ORDER BY p.name, b.name, u.unit_number
            LIMIT %(limit)s;
        """
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, p)
                return [dict(r) for r in cur.fetchall()]

    def get_summary_stats(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not data:
            return []
        total_units = len(data)
        occupied = sum(1 for r in data if r.get("occupancy_status") == "OCCUPIED")
        total_mkt = sum(float(r.get("market_rent") or 0) for r in data)
        total_contract = sum(float(r.get("contracted_rent") or 0) for r in data)
        occ_rate = (occupied / total_units * 100) if total_units else 0

        return [
            {"label": "Total Units", "value": f"{total_units:,}"},
            {"label": "Occupied Units", "value": f"{occupied:,}"},
            {"label": "Occupancy Rate", "value": f"{occ_rate:.1f}%"},
            {"label": "Total Market Rent", "value": f"₹{total_mkt:,.0f}"},
            {"label": "Total Contract Rent", "value": f"₹{total_contract:,.0f}"},
        ]
