from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ServiceRequestCreate(BaseModel):
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    location: str
    vehicle_type: Optional[str] = None
    issue: str


class ServiceRequestResponse(BaseModel):
    id: int
    tenant_id: Optional[str] = None
    location: str
    issue: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}