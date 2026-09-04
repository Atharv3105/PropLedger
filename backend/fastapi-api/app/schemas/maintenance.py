from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MaintenanceRequestResponse(BaseModel):
    request_id: int
    request_number: str
    unit_id: int
    unit_number: str
    property_name: str
    category: str
    priority: str
    status: str
    description: Optional[str] = None
    reported_date: Optional[datetime] = None

class MaintenanceReopenRequest(BaseModel):
    reopen_reason: str = Field(..., min_length=5, max_length=500)

class MaintenanceReopenResponse(BaseModel):
    request_id: int
    request_number: str
    new_status: str
    message: str
