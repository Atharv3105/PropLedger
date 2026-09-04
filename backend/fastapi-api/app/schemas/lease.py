from pydantic import BaseModel, Field, model_validator
from datetime import date
from typing import Optional
from decimal import Decimal

class ActiveLeaseResponse(BaseModel):
    lease_id: int
    lease_number: str
    unit_id: int
    unit_number: str
    building_name: str
    property_name: str
    tenant_id: int
    primary_tenant_name: str
    primary_tenant_email: Optional[str] = None
    primary_tenant_phone: Optional[str] = None
    start_date: date
    end_date: date
    monthly_rent: Decimal
    security_deposit: Decimal
    lease_status: str
    predecessor_lease_id: Optional[int] = None
    is_renewal: bool

class LeaseRenewRequest(BaseModel):
    new_start_date: date
    new_end_date: date
    new_monthly_rent: Decimal = Field(..., gt=0)
    
    @model_validator(mode="after")
    def validate_dates(self):
        if self.new_end_date <= self.new_start_date:
            raise ValueError("new_end_date must be strictly after new_start_date")
        return self

class LeaseRenewResponse(BaseModel):
    new_lease_id: int
    lease_number: str
    predecessor_lease_id: int
    message: str
