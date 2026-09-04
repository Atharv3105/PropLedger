from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class DelinquencyItem(BaseModel):
    tenant_id: int
    tenant_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    lease_id: int
    unit_number: str
    property_name: str
    current_0_30: Decimal
    past_due_31_60: Decimal
    past_due_61_90: Decimal
    severe_90_plus: Decimal
    total_delinquent_balance: Decimal
    max_overdue_days: int

class CollectionEscalateRequest(BaseModel):
    tenant_id: int
    lease_id: int
    case_notes: Optional[str] = "Delinquency escalated via API"

class CollectionEscalateResponse(BaseModel):
    collection_case_id: int
    tenant_id: int
    lease_id: int
    delinquent_amount: Decimal
    status: str
    message: str
