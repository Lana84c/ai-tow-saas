from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.deps import get_db
from app.db.models.dispatch_job import DispatchJob
from app.db.models.driver import Driver
from app.db.models.service_request import ServiceRequest
from app.schemas.dispatch import (
    DispatchJobResponse,
    DispatchStatusUpdate,
    DriverCreate,
    DriverLocationUpdate,
    DriverResponse,
)

from app.services.dispatch.assignment import assign_nearest_driver

from app.schemas.dispatch import (
    DispatchJobResponse,
    DispatchStatusUpdate,
    DriverCreate,
    DriverResponse,
)

from app.schemas.dispatch import (
    DispatchJobResponse,
    DriverCreate,
    DriverLocationUpdate,
    DriverResponse,
)

from app.services.notifications.sms import (
    notify_customer_driver_arriving,
    notify_customer_job_assigned,
    notify_customer_job_completed,
)

router = APIRouter()


@router.post("/drivers", response_model=DriverResponse)
def create_driver(
    payload: DriverCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    driver = Driver(
        tenant_id=tenant_id,
        name=payload.name,
        phone=payload.phone,
        truck_number=payload.truck_number,
        vehicle_type=payload.vehicle_type,
        current_latitude=payload.current_latitude,
        current_longitude=payload.current_longitude,
        is_available=payload.is_available,
    )

    db.add(driver)
    db.commit()
    db.refresh(driver)

    return driver


@router.get("/drivers", response_model=List[DriverResponse])
def list_drivers(
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    query = db.query(Driver)
    if tenant_id:
        query = query.filter(Driver.tenant_id == tenant_id)

    return query.order_by(Driver.id.desc()).all()

@router.patch("/drivers/{driver_id}/location", response_model=DriverResponse)
def update_driver_location(
    driver_id: int,
    payload: DriverLocationUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    query = db.query(Driver).filter(Driver.id == driver_id)
    if tenant_id:
        query = query.filter(Driver.tenant_id == tenant_id)

    driver = query.first()

    if not driver:
        raise HTTPException(status_code=404, detail="Driver not found")

    driver.current_latitude = payload.current_latitude
    driver.current_longitude = payload.current_longitude

    if payload.is_available is not None:
        driver.is_available = payload.is_available

    db.commit()
    db.refresh(driver)

    return driver

@router.post("/assign/{service_request_id}", response_model=DispatchJobResponse)
def assign_dispatch_job(
    service_request_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    query = db.query(ServiceRequest).filter(ServiceRequest.id == service_request_id)
    if tenant_id:
        query = query.filter(ServiceRequest.tenant_id == tenant_id)

    service_request = query.first()

    if not service_request:
        raise HTTPException(status_code=404, detail="Service request not found")

    driver, distance_miles, eta_minutes = assign_nearest_driver(
        db=db,
        service_request=service_request,
        tenant_id=tenant_id,
    )

    if not driver:
        raise HTTPException(status_code=404, detail="No available driver found")

    dispatch_job = DispatchJob(
        tenant_id=tenant_id,
        service_request_id=service_request.id,
        driver_id=driver.id,
        status="assigned",
        estimated_distance_miles=distance_miles,
        estimated_eta_minutes=eta_minutes,
    )

    service_request.status = "assigned"
    driver.is_available = False

    db.add(dispatch_job)
    db.commit()
    db.refresh(dispatch_job)

    notify_customer_job_assigned(service_request, driver, dispatch_job)

    return dispatch_job

@router.get("/jobs", response_model=List[DispatchJobResponse])
def list_dispatch_jobs(
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    query = db.query(DispatchJob)
    if tenant_id:
        query = query.filter(DispatchJob.tenant_id == tenant_id)

    return query.order_by(DispatchJob.id.desc()).all()

@router.patch("/jobs/{job_id}/status", response_model=DispatchJobResponse)
def update_dispatch_status(
    job_id: int,
    payload: DispatchStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    query = db.query(DispatchJob).filter(DispatchJob.id == job_id)

    if tenant_id:
        query = query.filter(DispatchJob.tenant_id == tenant_id)

    job = query.first()

    if not job:
        raise HTTPException(status_code=404, detail="Dispatch job not found")

    valid_statuses = [
        "assigned",
        "en_route",
        "arrived",
        "completed",
        "cancelled",
    ]

    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of {valid_statuses}",
        )

    job.status = payload.status

    service_request = db.query(ServiceRequest).filter(
        ServiceRequest.id == job.service_request_id
    ).first()

    if service_request:
        service_request.status = payload.status

    if payload.status in ["completed", "cancelled"]:
        driver = db.query(Driver).filter(Driver.id == job.driver_id).first()
        if driver:
            driver.is_available = True

    db.commit()
    db.refresh(job)

    if service_request and payload.status == "arrived":
        notify_customer_driver_arriving(service_request)

    if service_request and payload.status == "completed":
        notify_customer_job_completed(service_request)

    return job

@router.patch("/jobs/{job_id}/status", response_model=DispatchJobResponse)
def update_dispatch_status(
    job_id: int,
    payload: DispatchStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    query = db.query(DispatchJob).filter(DispatchJob.id == job_id)

    if tenant_id:
        query = query.filter(DispatchJob.tenant_id == tenant_id)

    job = query.first()

    if not job:
        raise HTTPException(status_code=404, detail="Dispatch job not found")

    valid_statuses = [
        "assigned",
        "en_route",
        "arrived",
        "completed",
        "cancelled",
    ]

    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of {valid_statuses}",
        )

    job.status = payload.status

    # if job completed, free the driver
    if payload.status in ["completed", "cancelled"]:
        driver = db.query(Driver).filter(Driver.id == job.driver_id).first()
        if driver:
            driver.is_available = True

    db.commit()
    db.refresh(job)

    return job

@router.post("/jobs/{dispatch_job_id}/status", response_model=DispatchJobResponse)
def update_dispatch_job_status(
    dispatch_job_id: int,
    payload: DispatchStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    tenant_id = getattr(request.state, "tenant_id", None)

    dispatch_query = db.query(DispatchJob).filter(DispatchJob.id == dispatch_job_id)
    if tenant_id:
        dispatch_query = dispatch_query.filter(DispatchJob.tenant_id == tenant_id)

    dispatch_job = dispatch_query.first()

    if not dispatch_job:
        raise HTTPException(status_code=404, detail="Dispatch job not found")

    service_request_query = db.query(ServiceRequest).filter(
        ServiceRequest.id == dispatch_job.service_request_id
    )
    if tenant_id:
        service_request_query = service_request_query.filter(
            ServiceRequest.tenant_id == tenant_id
        )
    service_request = service_request_query.first()

    driver = None
    if dispatch_job.driver_id is not None:
        driver_query = db.query(Driver).filter(Driver.id == dispatch_job.driver_id)
        if tenant_id:
            driver_query = driver_query.filter(Driver.tenant_id == tenant_id)
        driver = driver_query.first()

    dispatch_job.status = payload.status

    if service_request is not None:
        service_request.status = payload.status

    if payload.status in {"completed", "cancelled"} and driver is not None:
        driver.is_available = True

    db.commit()
    db.refresh(dispatch_job)

    return dispatch_job