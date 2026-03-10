from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.deps import get_db
from app.db.models.service_request import ServiceRequest
from app.integrations.maps_client import MapsClientError
from app.schemas.service_request import (
    ServiceRequestCreate,
    ServiceRequestResponse,
)
from app.services.geo.geocoder import resolve_address

router = APIRouter()


@router.post("/", response_model=ServiceRequestResponse)
def create_service_request(
    payload: ServiceRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    try:
        geo = resolve_address(payload.location)
    except MapsClientError as exc:
        raise HTTPException(status_code=400, detail=f"Location lookup failed: {exc}") from exc

    service_request = ServiceRequest(
        tenant_id=tenant_id,
        customer_name=payload.customer_name,
        phone=payload.phone,
        location=payload.location,
        formatted_address=geo.formatted_address,
        latitude=geo.latitude,
        longitude=geo.longitude,
        place_id=geo.place_id,
        vehicle_type=payload.vehicle_type,
        issue=payload.issue,
        status="pending",
    )

    db.add(service_request)
    db.commit()
    db.refresh(service_request)

    return service_request


@router.get("/", response_model=List[ServiceRequestResponse])
def list_requests(
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    query = db.query(ServiceRequest)

    if tenant_id:
        query = query.filter(ServiceRequest.tenant_id == tenant_id)

    return query.order_by(ServiceRequest.id.desc()).all()