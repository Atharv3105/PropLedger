from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class HierarchyNodeResponse(BaseModel):
    node_id: str
    parent_node_id: Optional[str] = None
    node_name: str
    node_type: str
    depth_level: int
    hierarchy_path: str

class RentPivotResponse(BaseModel):
    property_id: int
    property_code: str
    property_name: str
    billing_year: int
    jan_collected: Decimal
    feb_collected: Decimal
    mar_collected: Decimal
    apr_collected: Decimal
    may_collected: Decimal
    jun_collected: Decimal
    jul_collected: Decimal
    aug_collected: Decimal
    sep_collected: Decimal
    oct_collected: Decimal
    nov_collected: Decimal
    dec_collected: Decimal
    annual_total_collected: Decimal
