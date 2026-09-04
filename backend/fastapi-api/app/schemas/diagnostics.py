from pydantic import BaseModel
from typing import Dict, Any, List

class HealthResponse(BaseModel):
    status: str
    environment: str = "development"
    database: Dict[str, Any]
    pool: Dict[str, Any]
    timestamp: str

class IncidentResponse(BaseModel):
    incident_count: int
    recent_incidents: List[Dict[str, Any]]
