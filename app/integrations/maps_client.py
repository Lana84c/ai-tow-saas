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

        response = requests.post(url, params=params, json=payload, timeout=15)
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

        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            raise MapsClientError(f"Geocoding failed: {response.status_code} {response.text}")

        data = response.json()
        status = data.get("status")
        if status != "OK" or not data.get("results"):
            raise MapsClientError(f"Geocoding returned status={status}")

        return data["results"][0]