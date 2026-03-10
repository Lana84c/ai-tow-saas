from __future__ import annotations

from dataclasses import dataclass

from app.integrations.maps_client import MapsClient, MapsClientError


@dataclass
class GeocodeResult:
    input_address: str
    formatted_address: str
    latitude: float
    longitude: float
    place_id: str | None = None
    validation_possible: bool = False


def resolve_address(address: str) -> GeocodeResult:
    client = MapsClient()

    # Try Address Validation first
    try:
        validation_data = client.validate_address(address)
        result = validation_data.get("result", {})
        geocode = result.get("geocode", {})
        location = geocode.get("location", {})

        latitude = location.get("latitude")
        longitude = location.get("longitude")

        address_data = result.get("address", {})
        formatted_address = address_data.get("formattedAddress")

        if latitude is not None and longitude is not None and formatted_address:
            return GeocodeResult(
                input_address=address,
                formatted_address=formatted_address,
                latitude=float(latitude),
                longitude=float(longitude),
                place_id=geocode.get("placeId"),
                validation_possible=True,
            )
    except MapsClientError:
        pass

    # Fallback to Geocoding
    geocode_result = client.geocode_address(address)
    geometry = geocode_result["geometry"]["location"]

    return GeocodeResult(
        input_address=address,
        formatted_address=geocode_result.get("formatted_address", address),
        latitude=float(geometry["lat"]),
        longitude=float(geometry["lng"]),
        place_id=geocode_result.get("place_id"),
        validation_possible=False,
    )