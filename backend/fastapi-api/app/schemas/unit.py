from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class UnitResponse(BaseModel):
    unit_id: int
    building_id: int
    building_name: Optional[str] = None
    property_id: int
    property_name: Optional[str] = None
    unit_number: str
    unit_type: Optional[str] = None
    status: Optional[str] = None
    floor_number: Optional[int] = None
    square_feet: Optional[Decimal] = None
    market_rent: Decimal
    is_active: bool = True
