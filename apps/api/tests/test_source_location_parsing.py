from datetime import datetime, timezone

from app.sources.tuscia_sources import SourceConfig, _parse_listing_events


def test_listing_location_overrides_national_source_fallback():
    source = SourceConfig(
        "Eventi e Sagre",
        "https://www.eventiesagre.it/Eventi_Sagre/elenco.html",
        province="RM",
        region="Italia",
        latitude=41.9028,
        longitude=12.4964,
    )
    html = """
    <a href="/Eventi_Sagre/21020613_Sagra+del+Fungo+Porcino.html">
      Sagra del Fungo Porcino Con specialita Funghi Fritti A La Serra Di San Miniato
      Dal 25/09/2026 Al 27/09/2026 Toscana San Miniato (PI)
    </a>
    """

    events = _parse_listing_events(source, html, datetime(2026, 9, 23, tzinfo=timezone.utc))

    assert events
    assert events[0]["municipality"] == "San Miniato"
    assert events[0]["province"] == "PI"
    assert events[0]["region"] == "Toscana"


def test_eventiesagre_title_location_with_province_and_region():
    source = SourceConfig("Eventi e Sagre", "https://www.eventiesagre.it/Eventi_Sagre/elenco.html", province="RM", region="Italia")
    html = """
    <a href="/Eventi_Vari/cecima.html">
      26 Settembre 2026 - Trekking E Foliage Al Ponte Tibetano Di Cecima - Edizione Mattina a Cecima | 2026 | (PV) Lombardia | eventiesagre.it
    </a>
    """

    events = _parse_listing_events(source, html, datetime(2026, 9, 23, tzinfo=timezone.utc))

    assert events[0]["municipality"] == "Cecima"
    assert events[0]["province"] == "PV"
    assert events[0]["region"] == "Lombardia"


def test_sagrit_title_location_overrides_navigation_text():
    source = SourceConfig("Sagr.it", "https://sagr.it/eventi", province="RM", region="Italia")
    html = """
    <a href="/evento/lavello">
      Rveij d ru gran (Le vie del grano) 2026 2026 — Lavello | Sagr.it dal 26/09/2026 al 27/09/2026 Home - Basilicata - Pollino
    </a>
    <a href="/evento/serra">
      Festa del Fungo 2026 — Serra San Bruno | Sagr.it dal 26/09/2026 al 28/09/2026 Home - Calabria - Costa degli Dei
    </a>
    <a href="/evento/lignano">
      Lignano Tuna Festival 2026 — Lignano Sabbiadoro | Sagr.it dal 26/09/2026 al 27/09/2026 Home - Friuli Venezia Giulia
    </a>
    """

    events = _parse_listing_events(source, html, datetime(2026, 9, 23, tzinfo=timezone.utc))

    assert [(event["municipality"], event["province"], event["region"]) for event in events] == [
        ("Lavello", "PZ", "Basilicata"),
        ("Serra San Bruno", "VV", "Calabria"),
        ("Lignano Sabbiadoro", "UD", "Friuli Venezia Giulia"),
    ]
