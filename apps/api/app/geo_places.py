from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


DATA_PATH = Path(__file__).resolve().parent / "data" / "comuni_italiani.json"


@dataclass(frozen=True)
class GeoPlace:
    name: str
    municipality: str
    province: str
    region: str
    latitude: float
    longitude: float
    istat_code: str


def normalize_place_name(value: str | None) -> str:
    value = re.sub(r"^(comune|citta|città)\s+di\s+", "", value or "", flags=re.IGNORECASE)
    value = value.replace("’", "'")
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


@lru_cache(maxsize=1)
def load_places() -> tuple[GeoPlace, ...]:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        raw_places = json.load(handle)

    places: list[GeoPlace] = []
    for item in raw_places:
        coordinates = item.get("coordinate") or {}
        latitude = coordinates.get("lat")
        longitude = coordinates.get("lng")
        if latitude is None or longitude is None:
            continue
        province = item.get("sigla") or (item.get("provincia") or {}).get("sigla")
        region = (item.get("regione") or {}).get("nome")
        name = item.get("nome")
        istat_code = item.get("codice")
        if not name or not province or not region or not istat_code:
            continue
        places.append(
            GeoPlace(
                name=name,
                municipality=name,
                province=province,
                region=region,
                latitude=float(latitude),
                longitude=float(longitude),
                istat_code=istat_code,
            )
        )
    return tuple(places)


@lru_cache(maxsize=1)
def _places_by_name_province() -> dict[tuple[str, str], GeoPlace]:
    return {
        (normalize_place_name(place.municipality), place.province.casefold()): place
        for place in load_places()
    }


@lru_cache(maxsize=1)
def _places_by_name() -> dict[str, tuple[GeoPlace, ...]]:
    grouped: dict[str, list[GeoPlace]] = {}
    for place in load_places():
        grouped.setdefault(normalize_place_name(place.municipality), []).append(place)
    return {key: tuple(value) for key, value in grouped.items()}


def find_municipality(municipality: str | None, province: str | None = None, region: str | None = None) -> GeoPlace | None:
    normalized_name = normalize_place_name(municipality)
    if not normalized_name:
        return None

    if province:
        match = _places_by_name_province().get((normalized_name, province.casefold()))
        if match:
            return match

    matches = list(_places_by_name().get(normalized_name, ()))
    if region:
        normalized_region = normalize_place_name(region)
        regional_matches = [place for place in matches if normalize_place_name(place.region) == normalized_region]
        if len(regional_matches) == 1:
            return regional_matches[0]

    if len(matches) == 1:
        return matches[0]
    return None


def search_places(query: str, limit: int = 8) -> list[GeoPlace]:
    normalized = normalize_place_name(query)
    if len(normalized) < 2:
        return []

    places = load_places()
    exact = [place for place in places if normalize_place_name(place.name) == normalized]
    starts = [place for place in places if normalize_place_name(place.name).startswith(normalized) and place not in exact]
    contains = [place for place in places if normalized in normalize_place_name(place.name) and place not in exact and place not in starts]
    return [*exact, *starts, *contains][:limit]
