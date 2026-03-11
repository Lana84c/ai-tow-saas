from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.services.realtime.connection_manager import manager

from app.api.deps import get_db, require_roles
from app.db.models.dispatch_job import DispatchJob
from app.db.models.driver import Driver
from app.db.models.service_request import ServiceRequest
from app.db.models.user import User
from app.schemas.dispatch import (
    DispatchJobResponse,
    DispatchStatusUpdate,
    DriverLocationUpdate,
    DriverResponse,
)

router = APIRouter()


def get_current_driver_for_user(db: Session, current_user: User) -> Driver:
    driver = (
        db.query(Driver)
        .filter(
            Driver.user_id == current_user.id,
            Driver.tenant_id == current_user.tenant_id,
        )
        .first()
    )

    if not driver:
        raise HTTPException(status_code=404, detail="Driver profile not found")

    return driver


@router.get("/jobs", response_model=List[DispatchJobResponse])
def get_my_driver_jobs(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("driver")),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    driver = get_current_driver_for_user(db, current_user)

    query = db.query(DispatchJob).filter(DispatchJob.driver_id == driver.id)

    if tenant_id:
        query = query.filter(DispatchJob.tenant_id == tenant_id)

    return query.order_by(DispatchJob.id.desc()).all()


@router.patch("/location", response_model=DriverResponse)
async def update_my_driver_location(
    payload: DriverLocationUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("driver")),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    driver = get_current_driver_for_user(db, current_user)

    if tenant_id and driver.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Tenant mismatch")

    driver.current_latitude = payload.current_latitude
    driver.current_longitude = payload.current_longitude

    if payload.is_available is not None:
        driver.is_available = payload.is_available

    db.commit()
    db.refresh(driver)

    if tenant_id:
        await manager.broadcast_to_tenant(
            tenant_id,
            {
                "type": "driver_location_update",
                "driver_id": driver.id,
                "name": driver.name,
                "truck_number": driver.truck_number,
                "latitude": driver.current_latitude,
                "longitude": driver.current_longitude,
                "available": driver.is_available,
            },
        )

    return driver

@router.patch("/jobs/{job_id}/status", response_model=DispatchJobResponse)
def update_my_job_status(
    job_id: int,
    payload: DispatchStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles("driver")),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    driver = get_current_driver_for_user(db, current_user)

    query = db.query(DispatchJob).filter(
        DispatchJob.id == job_id,
        DispatchJob.driver_id == driver.id,
    )

    if tenant_id:
        query = query.filter(DispatchJob.tenant_id == tenant_id)

    job = query.first()

    if not job:
        raise HTTPException(status_code=404, detail="Driver job not found")

    valid_statuses = ["en_route", "arrived", "completed"]

    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of {valid_statuses}",
        )

    job.status = payload.status

    service_request = (
        db.query(ServiceRequest)
        .filter(ServiceRequest.id == job.service_request_id)
        .first()
    )
    if service_request:
        service_request.status = payload.status

    if payload.status == "completed":
        driver.is_available = True

    db.commit()
    db.refresh(job)

    return job