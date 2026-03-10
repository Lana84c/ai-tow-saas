from __future__ import annotations

from typing import Any

import requests

from app.core.config import settings


class MapsClientError(Exception):
    pass


class MapsClient:
    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or settings.GOOGLE_MAPS_API_KEY
        if not self.api_key:
            raise MapsClientError("GOOGLE_MAPS_API_KEY is not configured.")

    def validate_address(self, address: str, region_code: str = "US") -> dict[str, Any]:
        url = "https://addressvalidation.googleapis.com/v1:validateAddress"
        params = {"key": self.api_key}
        payload = {
            "address": {
                "regionCode": region_code,
                "addressLines": [address],
            }
        }

        try:
            response = requests.post(url, params=params, json=payload, timeout=15)
        except requests.RequestException as exc:
            raise MapsClientError(f"Address validation request failed: {exc}") from exc

        if response.status_code != 200:
            raise MapsClientError(
                f"Address validation failed: {response.status_code} {response.text}"
            )

        return response.json()

    def geocode_address(self, address: str) -> dict[str, Any]:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": address,
            "key": self.api_key,
        }

        try:
            response = requests.get(url, params=params, timeout=15)
        except requests.RequestException as exc:
            raise MapsClientError(f"Geocoding request failed: {exc}") from exc

        if response.status_code != 200:
            raise MapsClientError(f"Geocoding failed: {response.status_code} {response.text}")

        data = response.json()
        status = data.get("status")
        if status != "OK" or not data.get("results"):
            raise MapsClientError(f"Geocoding returned status={status}")

        return data["results"][0]

    def compute_driving_route(
        self,
        origin_lat: float,
        origin_lng: float,
        destination_lat: float,
        destination_lng: float,
        traffic_aware: bool = True,
    ) -> dict[str, Any]:
        url = "https://routes.googleapis.com/directions/v2:computeRoutes"

        routing_preference = "TRAFFIC_AWARE" if traffic_aware else "TRAFFIC_UNAWARE"

        payload = {
            "origin": {
                "location": {
                    "latLng": {
                        "latitude": origin_lat,
                        "longitude": origin_lng,
                    }
                }
            },
            "destination": {
                "location": {
                    "latLng": {
                        "latitude": destination_lat,
                        "longitude": destination_lng,
                    }
                }
            },
            "travelMode": "DRIVE",
            "routingPreference": routing_preference,
            "units": "IMPERIAL",
        }

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "routes.duration,routes.distanceMeters",
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=20)
        except requests.RequestException as exc:
            raise MapsClientError(f"Compute Routes request failed: {exc}") from exc

        if response.status_code != 200:
            raise MapsClientError(
                f"Compute Routes failed: {response.status_code} {response.text}"
            )

        data = response.json()
        routes = data.get("routes", [])
        if not routes:
            raise MapsClientError("Compute Routes returned no routes")

        return routes[0]