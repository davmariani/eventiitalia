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
