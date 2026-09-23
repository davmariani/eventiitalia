import os

os.environ.setdefault("DATABASE_URL", "sqlite://")

from app.geo_places import find_municipality, search_places
from app.routers.events import ALLOWED_RADII_KM, haversine_km


def test_search_places_finds_ambiguous_label_details():
    results = search_places("Roma")

    assert results
    assert results[0].municipality == "Roma"
    assert results[0].province == "RM"
    assert results[0].region == "Lazio"
    assert results[0].istat_code


def test_search_places_uses_full_municipality_archive():
    results = search_places("Cecima")

    assert results
    assert results[0].municipality == "Cecima"
    assert results[0].province == "PV"
    assert results[0].region == "Lombardia"
    assert results[0].latitude is not None
    assert results[0].longitude is not None


def test_find_municipality_by_name_and_province():
    place = find_municipality("San Miniato", "PI", "Toscana")

    assert place is not None
    assert place.municipality == "San Miniato"
    assert place.province == "PI"
    assert place.region == "Toscana"


def test_allowed_radii_match_frontend_options():
    assert ALLOWED_RADII_KM == {10, 25, 50, 75, 100, 150, 200, 300, 500}


def test_haversine_distance_is_in_kilometers():
    distance = haversine_km(41.9028, 12.4964, 45.4642, 9.19)

    assert 470 <= distance <= 490
