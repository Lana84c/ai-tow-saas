from __future__ import annotations

from dataclasses import dataclass

from app.core.config import settings
from app.integrations.maps_client import MapsClient, MapsClientError


@dataclass
class EtaResult:
    distance_miles: float
    eta_minutes: int
    source: str  # "google_routes" or "fallback"


def estimate_eta_minutes(distance_miles: float, avg_speed_mph: float = 25.0) -> int:
    if distance_miles <= 0:
        return 1

    hours = distance_miles / avg_speed_mph
    minutes = round(hours * 60)

    return max(minutes, 1)


def meters_to_miles(meters: float) -> float:
    return meters * 0.000621371


def parse_duration_to_minutes(duration_value: str) -> int:
    """
    Google Routes returns durations as strings like '123s'.
    """
    if not duration_value.endswith("s"):
        raise ValueError(f"Unexpected duration format: {duration_value}")

    seconds = float(duration_value[:-1])
    minutes = round(seconds / 60)

    return max(minutes, 1)


def compute_eta_with_google_routes(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
) -> EtaResult:
    client = MapsClient()

    route = client.compute_driving_route(
        origin_lat=origin_lat,
        origin_lng=origin_lng,
        destination_lat=destination_lat,
        destination_lng=destination_lng,
        traffic_aware=settings.GOOGLE_ROUTES_TRAFFIC_AWARE,
    )

    distance_meters = route.get("distanceMeters")
    duration_value = route.get("duration")

    if distance_meters is None or duration_value is None:
        raise MapsClientError("Routes response missing distance or duration")

    distance_miles = round(meters_to_miles(float(distance_meters)), 2)
    eta_minutes = parse_duration_to_minutes(duration_value)

    return EtaResult(
        distance_miles=distance_miles,
        eta_minutes=eta_minutes,
        source="google_routes",
    )