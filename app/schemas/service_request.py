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
    formatted_address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    place_id: Optional[str] = None
    issue: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}