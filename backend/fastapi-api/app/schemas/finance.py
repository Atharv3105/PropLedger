from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

class ExpenseResponse(BaseModel):
    expense_id: int
    property_id: int
    property_name: str
    vendor_name: Optional[str] = None
    category: str
    amount: Decimal
    expense_date: date
    description: Optional[str] = None

class FinancialSummaryResponse(BaseModel):
    property_id: int
    property_code: str
    property_name: str
    property_type: Optional[str] = None
    city: Optional[str] = None
    owner_name: Optional[str] = None
    total_billed_rent: Decimal
    total_collected_rent: Decimal
    total_late_fees_collected: Decimal
    total_operating_revenue: Decimal
    total_operating_expenses: Decimal
    net_operating_income: Decimal
    collection_percentage: Optional[Decimal] = None
