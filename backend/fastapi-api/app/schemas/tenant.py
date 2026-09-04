from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class TenantResponse(BaseModel):
    tenant_id: int
    first_name: str
    last_name: str
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    credit_score: Optional[int] = None
    is_active: bool = True

class TenantBalanceResponse(BaseModel):
    tenant_id: int
    tenant_name: str
    tenant_email: Optional[str] = None
    tenant_phone: Optional[str] = None
    lease_id: int
    property_name: str
    unit_number: str
    lease_status: str
    total_billed: Decimal
    total_paid: Decimal
    total_late_fees: Decimal
    outstanding_balance: Decimal
