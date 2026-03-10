from sqlalchemy.orm import Session

from app.db.models.driver import Driver
from app.db.models.service_request import ServiceRequest
from app.integrations.maps_client import MapsClientError
from app.services.dispatch.eta import get_route_eta_and_distance
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

        try:
            route_distance, route_eta = get_route_eta_and_distance(
                origin_lat=driver.current_latitude,
                origin_lng=driver.current_longitude,
                destination_lat=service_request.latitude,
                destination_lng=service_request.longitude,
            )
            distance = route_distance
            eta = route_eta
        except MapsClientError:
            # fallback if Routes API fails
            distance = round(
                haversine_miles(
                    service_request.latitude,
                    service_request.longitude,
                    driver.current_latitude,
                    driver.current_longitude,
                ),
                2,
            )
            eta = max(round((distance / 25.0) * 60), 1)

        if best_distance is None or distance < best_distance:
            best_driver = driver
            best_distance = distance
            best_eta = eta

    if best_driver is None or best_distance is None or best_eta is None:
        return None, None, None

    return best_driver, best_distance, best_eta