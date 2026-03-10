from __future__ import annotations

from app.db.models.dispatch_job import DispatchJob
from app.db.models.driver import Driver
from app.db.models.service_request import ServiceRequest
from app.integrations.twilio_client import TwilioClientError, send_sms


def notify_customer_job_assigned(
    service_request: ServiceRequest,
    driver: Driver,
    dispatch_job: DispatchJob,
) -> str | None:
    if not service_request.phone:
        return None

    message = (
        f"Your tow request has been assigned. "
        f"Driver: {driver.name}. "
        f"Truck: {driver.truck_number or 'N/A'}. "
        f"ETA: {dispatch_job.estimated_eta_minutes or 'unknown'} minutes."
    )

    try:
        return send_sms(service_request.phone, message)
    except TwilioClientError as exc:
        print(f"SMS assignment notification failed: {exc}")
        return None


def notify_customer_driver_arriving(service_request: ServiceRequest) -> str | None:
    if not service_request.phone:
        return None

    message = "Your tow driver has arrived."

    try:
        return send_sms(service_request.phone, message)
    except TwilioClientError as exc:
        print(f"SMS arrival notification failed: {exc}")
        return None


def notify_customer_job_completed(service_request: ServiceRequest) -> str | None:
    if not service_request.phone:
        return None

    message = "Your tow service has been completed. Thank you for choosing us."

    try:
        return send_sms(service_request.phone, message)
    except TwilioClientError as exc:
        print(f"SMS completion notification failed: {exc}")
        return None