from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel


class DriverCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    truck_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    current_latitude: float
    current_longitude: float
    is_available: bool = True


class DriverResponse(BaseModel):
    id: int
    tenant_id: Optional[str] = None
    name: str
    phone: Optional[str] = None
    truck_number: Optional[str] = None
    vehicle_type: Optional[str] = None
    current_latitude: Optional[float] = None
    current_longitude: Optional[float] = None
    is_available: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DispatchJobResponse(BaseModel):
    id: int
    tenant_id: Optional[str] = None
    service_request_id: int
    driver_id: Optional[int] = None
    status: str
    estimated_distance_miles: Optional[float] = None
    estimated_eta_minutes: Optional[int] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DispatchStatusUpdate(BaseModel):
    status: Literal["en_route", "arrived", "completed", "cancelled"]