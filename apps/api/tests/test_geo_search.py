from app.geo_places import search_places
from app.routers.events import ALLOWED_RADII_KM, haversine_km


def test_search_places_finds_ambiguous_label_details():
    results = search_places("Roma")

    assert results
    assert results[0].municipality == "Roma"
    assert results[0].province == "RM"
    assert results[0].region == "Lazio"
    assert results[0].istat_code


def test_allowed_radii_match_frontend_options():
    assert ALLOWED_RADII_KM == {10, 25, 50, 75, 100, 150, 200, 300, 500}


def test_haversine_distance_is_in_kilometers():
    distance = haversine_km(41.9028, 12.4964, 45.4642, 9.19)

    assert 470 <= distance <= 490
