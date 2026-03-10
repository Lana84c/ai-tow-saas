from app.integrations.maps_client import MapsClient, MapsClientError


def meters_to_miles(meters: float) -> float:
    return meters * 0.000621371


def duration_to_minutes(duration_str: str) -> int:
    # Example: "305s"
    seconds = int(duration_str.rstrip("s"))
    minutes = round(seconds / 60)
    return max(minutes, 1)


def get_route_eta_and_distance(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
) -> tuple[float, int]:
    client = MapsClient()

    route = client.compute_driving_route(
        origin_lat=origin_lat,
        origin_lng=origin_lng,
        destination_lat=destination_lat,
        destination_lng=destination_lng,
    )

    distance_meters = route.get("distanceMeters")
    duration_str = route.get("duration")

    if distance_meters is None or duration_str is None:
        raise MapsClientError("Routes API response missing distance or duration")

    distance_miles = round(meters_to_miles(float(distance_meters)), 2)
    eta_minutes = duration_to_minutes(duration_str)

    return distance_miles, eta_minutes