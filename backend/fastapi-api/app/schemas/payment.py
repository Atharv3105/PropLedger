from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List
from decimal import Decimal

class PaymentCreateRequest(BaseModel):
    lease_id: int
    amount: Decimal = Field(..., gt=0, description="Payment amount must be strictly greater than zero per Rule BR-10")
    payment_date: Optional[date] = None
    payment_method_id: int = Field(default=1, description="1=BANK_TRANSFER, 2=CHECK, 3=CREDIT_CARD, etc.")
    reference_number: Optional[str] = None
    notes: Optional[str] = None

class PaymentAllocationItem(BaseModel):
    allocation_id: int
    charge_id: int
    charge_type: Optional[str] = None
    amount_allocated: Decimal

class PaymentResponse(BaseModel):
    payment_id: int
    lease_id: int
    amount_paid: Decimal
    allocated_amount: Decimal
    unallocated_amount: Decimal
    remaining_balance: Decimal
    allocations_count: int
    message: str

class TenantPaymentHistoryItem(BaseModel):
    payment_id: int
    lease_id: int
    payment_date: date
    payment_method: str
    payment_amount: Decimal
    running_total_paid: Decimal
    days_since_last_payment: Optional[int] = None
    payment_rank: int
