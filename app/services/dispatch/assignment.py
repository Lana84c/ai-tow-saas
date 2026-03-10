from sqlalchemy.orm import Session

from app.db.models.driver import Driver
from app.db.models.service_request import ServiceRequest
from app.services.dispatch.eta import estimate_eta_minutes
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

    for driver in drivers:
        if driver.current_latitude is None or driver.current_longitude is None:
            continue

        distance = haversine_miles(
            service_request.latitude,
            service_request.longitude,
            driver.current_latitude,
            driver.current_longitude,
        )

        if best_distance is None or distance < best_distance:
            best_driver = driver
            best_distance = distance

    if best_driver is None or best_distance is None:
        return None, None, None

    eta_minutes = estimate_eta_minutes(best_distance)

    return best_driver, round(best_distance, 2), eta_minutes