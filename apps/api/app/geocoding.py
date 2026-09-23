from __future__ import annotations

import time
from dataclasses import dataclass, field

import httpx

from app.config import settings
from app.models import Location


@dataclass
class Geocoder:
    cache: dict[tuple[str, str, str], tuple[float, float] | None] = field(default_factory=dict)
    requests_made: int = 0
    last_request_at: float = 0.0

    def lookup(self, municipality: str | None, province: str | None, region: str | None) -> tuple[float, float] | None:
        if not settings.geocoding_enabled or not municipality:
            return None

        key = (
            municipality.strip().casefold(),
            (province or "").strip().casefold(),
            (region or "").strip().casefold(),
        )
        if key in self.cache:
            return self.cache[key]
        if self.requests_made >= settings.geocoding_max_requests_per_refresh:
            self.cache[key] = None
            return None

        query_parts = [municipality, province, region, "Italia"]
        query = ", ".join(part for part in query_parts if part)
        elapsed = time.monotonic() - self.last_request_at
        if self.last_request_at and elapsed < 1.1:
            time.sleep(1.1 - elapsed)

        params: dict[str, str | int] = {
            "q": query,
            "format": "jsonv2",
            "limit": 1,
            "countrycodes": "it",
        }
        if settings.nominatim_email:
            params["email"] = settings.nominatim_email

        self.requests_made += 1
        self.last_request_at = time.monotonic()
        try:
            response = httpx.get(
                settings.nominatim_url,
                params=params,
                timeout=8,
                headers={"User-Agent": settings.nominatim_user_agent},
            )
            response.raise_for_status()
            items = response.json()
        except (httpx.HTTPError, ValueError):
            self.cache[key] = None
            return None

        if not items:
            self.cache[key] = None
            return None

        try:
            coordinates = (float(items[0]["lat"]), float(items[0]["lon"]))
        except (KeyError, TypeError, ValueError):
            coordinates = None
        self.cache[key] = coordinates
        return coordinates


def cached_location_coordinates(location: Location | None) -> tuple[float, float] | None:
    if location and location.latitude is not None and location.longitude is not None:
        return location.latitude, location.longitude
    return None
