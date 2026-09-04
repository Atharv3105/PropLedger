from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class PropertyCreate(BaseModel):
    property_code: str = Field(..., max_length=50)
    property_name: str = Field(..., max_length=200)
    property_type: str = Field("COMMERCIAL", max_length=50)
    address_line1: str = Field(..., max_length=255)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: str = Field(..., max_length=20)
    year_built: Optional[int] = Field(None, ge=1800, le=2100)
    total_area_sqft: Optional[Decimal] = Field(None, gt=0)

class PropertyResponse(BaseModel):
    property_id: int
    property_code: str
    property_name: str
    property_type: Optional[str] = None
    address_line1: str
    city: str
    state: str
    postal_code: str
    year_built: Optional[int] = None
    total_area_sqft: Optional[Decimal] = None
    total_buildings: int = 0
    total_units: int = 0

class BuildingResponse(BaseModel):
    building_id: int
    property_id: int
    property_name: Optional[str] = None
    building_code: str
    building_name: str
    total_floors: Optional[int] = None
    total_units: int = 0

class PropertyOccupancyStats(BaseModel):
    property_id: int
    property_code: str
    property_name: str
    total_units: int
    occupied_units: int
    vacant_units: int
    under_maintenance_units: int
    occupancy_rate_pct: Decimal
