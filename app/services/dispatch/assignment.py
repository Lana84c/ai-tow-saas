from sqlalchemy.orm import Session

from app.db.models.driver import Driver
from app.db.models.service_request import ServiceRequest
from app.integrations.maps_client import MapsClientError
from app.services.dispatch.eta import (
    compute_eta_with_google_routes,
    estimate_eta_minutes,
)
from app.services.geo.distance import haversine_miles


def assign_nearest_driver(
    db: Session,
    service_request: ServiceRequest,
    tenant_id: str | None = None,
) -> tuple[Driver | None, float | None, int | None]:
    if service_request.latitude is None or service_request.longitude is None:
        return None, None, None

    query = db.query(Driver).filter(Driver.is_available == True)  # noqa: E712

    if tenant_id:
        query = query.filter(Driver.tenant_id == tenant_id)

    drivers = query.all()

    best_driver = None
    best_distance = None
    best_eta = None

    for driver in drivers:
        if driver.current_latitude is None or driver.current_longitude is None:
            continue

        # Fast candidate scoring by straight-line distance first
        crow_distance = haversine_miles(
            service_request.latitude,
            service_request.longitude,
            driver.current_latitude,
            driver.current_longitude,
        )

        if best_distance is not None and crow_distance >= best_distance:
            continue

        try:
            eta_result = compute_eta_with_google_routes(
                origin_lat=driver.current_latitude,
                origin_lng=driver.current_longitude,
                destination_lat=service_request.latitude,
                destination_lng=service_request.longitude,
            )
            actual_distance = eta_result.distance_miles
            actual_eta = eta_result.eta_minutes
        except MapsClientError:
            actual_distance = round(crow_distance, 2)
            actual_eta = estimate_eta_minutes(actual_distance)

        if best_eta is None or actual_eta < best_eta:
            best_driver = driver
            best_distance = actual_distance
            best_eta = actual_eta

    if best_driver is None or best_distance is None or best_eta is None:
        return None, None, None

    return best_driver, best_distance, best_eta