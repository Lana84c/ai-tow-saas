from typing import List

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.deps import get_db
from app.db.models.service_request import ServiceRequest
from app.schemas.service_request import (
    ServiceRequestCreate,
    ServiceRequestResponse,
)

router = APIRouter()


@router.post("/", response_model=ServiceRequestResponse)
def create_service_request(
    payload: ServiceRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    service_request = ServiceRequest(
        tenant_id=tenant_id,
        customer_name=payload.customer_name,
        phone=payload.phone,
        location=payload.location,
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