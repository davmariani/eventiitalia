from app.geocoding import _result_matches_municipality


def test_result_matches_exact_municipality():
    item = {"address": {"village": "Cecima"}, "display_name": "Cecima, Pavia, Lombardia, Italia"}

    assert _result_matches_municipality(item, "Cecima")


def test_result_rejects_unrelated_municipality():
    item = {"address": {"city": "Roma"}, "display_name": "Roma, Lazio, Italia"}

    assert not _result_matches_municipality(item, "Cecima")
