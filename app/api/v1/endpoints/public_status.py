from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models.service_request import ServiceRequest
from app.db.models.dispatch_job import DispatchJob
from app.db.models.driver import Driver

router = APIRouter()


@router.get("/status/{service_request_id}")
def get_customer_status(service_request_id: int, db: Session = Depends(get_db)):
    request = db.query(ServiceRequest).filter(
        ServiceRequest.id == service_request_id
    ).first()

    if not request:
        raise HTTPException(status_code=404, detail="Service request not found")

    job = db.query(DispatchJob).filter(
        DispatchJob.service_request_id == service_request_id
    ).first()

    driver = None
    if job and job.driver_id:
        driver = db.query(Driver).filter(Driver.id == job.driver_id).first()

    return {
        "request_id": request.id,
        "status": request.status,
        "location": request.formatted_address,
        "driver": {
            "name": driver.name if driver else None,
            "truck_number": driver.truck_number if driver else None,
        } if driver else None,
        "eta_minutes": job.estimated_eta_minutes if job else None,
        "distance_miles": job.estimated_distance_miles if job else None,
    }