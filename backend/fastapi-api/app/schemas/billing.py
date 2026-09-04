from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class GenerateRentRequest(BaseModel):
    billing_month: int = Field(..., ge=1, le=12)
    billing_year: int = Field(..., ge=2000, le=2100)

class GenerateRentResponse(BaseModel):
    billing_month: int
    billing_year: int
    charges_created: int
    total_amount: Decimal
    message: str
