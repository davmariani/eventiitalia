from __future__ import annotations

from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.database import Base
from app.models import Category, Event, EventSource, Location
from app.sources.comune_viterbo import fetch_comune_viterbo_events
from app.sources.tuscia_sources import SourceConfig, fetch_all_abruzzo_events, fetch_all_tuscany_events, fetch_all_tuscia_events, fetch_all_umbria_events, fetch_source_events


DEMO_EVENTS = [
    {
        "slug": "sagra-della-castagna-vallerano",
        "title": "Sagra della Castagna",
        "short_description": "Manifestazione enogastronomica con degustazioni e mercatini.",
        "description": "Evento dedicato alla castagna e alle tradizioni locali.",
        "is_free": True,
        "source_name": "Comune di Vallerano",
        "source_url": "https://example.com/fonte",
        "official_url": "https://example.com/evento",
        "latitude": 42.345,
        "longitude": 12.234,
        "published": True,
        "category_name": "Sagre",
        "municipality": "Vallerano",
        "province": "VT",
        "region": "Lazio",
        "day_offset": 0,
        "start_hour": 10,
        "duration_hours": 10,
    },
    {
        "slug": "mercatino-di-castel-gandolfo",
        "title": "Mercatino di Castel Gandolfo",
        "short_description": "Passeggiata, artigianato e prodotti locali.",
        "description": "Mercatino con bancarelle e prodotti tipici del territorio.",
        "is_free": True,
        "source_name": "Comune di Castel Gandolfo",
        "source_url": "https://example.com/fonte-2",
        "official_url": "https://example.com/evento-2",
        "latitude": 41.747,
        "longitude": 12.646,
        "published": True,
        "category_name": "Mercatini",
        "municipality": "Castel Gandolfo",
        "province": "RM",
        "region": "Lazio",
        "day_offset": 2,
        "start_hour": 9,
        "duration_hours": 10,
    },
    {
        "slug": "notte-della-musica-roma",
        "title": "Notte della Musica",
        "short_description": "Serata musicale con concerti e dj set.",
        "description": "Una serata all'aperto con artisti e performance musicali.",
        "is_free": False,
        "source_name": "Roma Eventi",
        "source_url": "https://example.com/fonte-3",
        "official_url": "https://example.com/evento-3",
        "latitude": 41.9028,
        "longitude": 12.4964,
        "published": True,
        "category_name": "Concerti",
        "municipality": "Roma",
        "province": "RM",
        "region": "Lazio",
        "day_offset": 5,
        "start_hour": 20,
        "duration_hours": 6,
    },
    {
        "slug": "fiera-del-raccolto-casale",
        "title": "Fiera del Raccolto",
        "short_description": "Mostra agricola e degustazioni di prodotti locali.",
        "description": "Manifestazione contadina con stand, mercati e assaggi.",
        "is_free": True,
        "source_name": "Provincia di Torino",
        "source_url": "https://example.com/fonte-4",
        "official_url": "https://example.com/evento-4",
        "latitude": 45.0703,
        "longitude": 7.6869,
        "published": True,
        "category_name": "Fiere",
        "municipality": "Casale",
        "province": "TO",
        "region": "Piemonte",
        "day_offset": 8,
        "start_hour": 9,
        "duration_hours": 33,
    },
    {
        "slug": "festa-dell-uva-bolzano",
        "title": "Festa dell'Uva",
        "short_description": "Degustazioni, mostre e musica in piazza.",
        "description": "Manifestazione estiva con eventi enogastronomici e spettacoli.",
        "is_free": True,
        "source_name": "Provincia di Bolzano",
        "source_url": "https://example.com/fonte-5",
        "official_url": "https://example.com/evento-5",
        "latitude": 46.4983,
        "longitude": 11.3548,
        "published": True,
        "category_name": "Feste",
        "municipality": "Bolzano",
        "province": "BZ",
        "region": "Trentino-Alto Adige",
        "day_offset": 12,
        "start_hour": 17,
        "duration_hours": 7,
    },
    {
        "slug": "mostra-mercato-umbria",
        "title": "Mostra Mercato dell'Artigianato",
        "short_description": "Bancarelle e artigianato locale.",
        "description": "Giornata di shopping, artigianato e degustazioni.",
        "is_free": True,
        "source_name": "Umbria Eventi",
        "source_url": "https://example.com/fonte-6",
        "official_url": "https://example.com/evento-6",
        "latitude": 43.1121,
        "longitude": 12.3887,
        "published": True,
        "category_name": "Mostre",
        "municipality": "Perugia",
        "province": "PG",
        "region": "Umbria",
        "day_offset": 17,
        "start_hour": 10,
        "duration_hours": 8,
    },
    {
        "slug": "fiera-di-cinema-napoli",
        "title": "Fiera del Cinema e delle Arti",
        "short_description": "Cortometraggi, proiezioni e incontri.",
        "description": "Dedicata a film, cultura e incontri con gli autori.",
        "is_free": False,
        "source_name": "Napoli Cultura",
        "source_url": "https://example.com/fonte-7",
        "official_url": "https://example.com/evento-7",
        "latitude": 40.8518,
        "longitude": 14.2681,
        "published": True,
        "category_name": "Mostre",
        "municipality": "Napoli",
        "province": "NA",
        "region": "Campania",
        "day_offset": 21,
        "start_hour": 18,
        "duration_hours": 5,
    },
    {
        "slug": "mercatino-vegano-firenze",
        "title": "Mercatino del Bio",
        "short_description": "Prodotti biologici e artigianato locale.",
        "description": "Mercato di prodotti biologici, artigianato e street food.",
        "is_free": True,
        "source_name": "Firenze Market",
        "source_url": "https://example.com/fonte-8",
        "official_url": "https://example.com/evento-8",
        "latitude": 43.7696,
        "longitude": 11.2558,
        "published": True,
        "category_name": "Mercatini",
        "municipality": "Firenze",
        "province": "FI",
        "region": "Toscana",
        "day_offset": 26,
        "start_hour": 9,
        "duration_hours": 9,
    },
    {
        "slug": "concerto-in-piazza-palermo",
        "title": "Concerto in Piazza",
        "short_description": "Serata musicale con gruppi locali.",
        "description": "Una serata all'insegna di musica, street food e convivialità.",
        "is_free": True,
        "source_name": "Palermo Musica",
        "source_url": "https://example.com/fonte-9",
        "official_url": "https://example.com/evento-9",
        "latitude": 38.1157,
        "longitude": 13.3615,
        "published": True,
        "category_name": "Concerti",
        "municipality": "Palermo",
        "province": "PA",
        "region": "Sicilia",
        "day_offset": 31,
        "start_hour": 19,
        "duration_hours": 4,
    },
]


def _build_demo_events(reference_now: datetime | None = None) -> list[dict]:
    now = (reference_now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    window_end = now + timedelta(days=90)

    built_events: list[dict] = []
    for payload in DEMO_EVENTS:
        starts_at = now + timedelta(days=payload["day_offset"], hours=payload["start_hour"])
        ends_at = starts_at + timedelta(hours=payload["duration_hours"])

        if ends_at < now or starts_at > window_end:
            continue

        built_events.append(
            {
                **payload,
                "starts_at": starts_at,
                "ends_at": ends_at,
            }
        )

    return built_events


def get_event_window(reference_now: datetime | None = None) -> tuple[datetime, datetime]:
    now = (reference_now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    return now, now + timedelta(days=90)


def _ensure_category(session: Session, name: str) -> Category:
    category = session.execute(select(Category).where(Category.slug == name.lower().replace(" ", "-")).limit(1)).scalar_one_or_none()
    if category is None:
        category = Category(name=name, slug=name.lower().replace(" ", "-"), icon_key=name.lower()[:3])
        session.add(category)
        session.flush()
    return category


def _ensure_location(session: Session, municipality: str, province: str, region: str, latitude: float | None, longitude: float | None) -> Location:
    location = session.execute(
        select(Location).where(
            Location.municipality == municipality,
            Location.province == province,
            Location.region == region,
        ).limit(1)
    ).scalar_one_or_none()
    if location is None:
        location = Location(
            municipality=municipality,
            province=province,
            region=region,
            latitude=latitude,
            longitude=longitude,
        )
        session.add(location)
        session.flush()
    return location


def refresh_demo_data(session: Session) -> int:
    Base.metadata.create_all(bind=session.bind)
    session.execute(delete(Event))
    session.flush()

    start_at, end_at = get_event_window()
    source_events: list[dict] = []
    try:
        source_events.extend(fetch_comune_viterbo_events(start_at))
    except Exception:
        pass
    try:
        source_events.extend(fetch_all_tuscia_events(start_at))
    except Exception:
        pass
    try:
        source_events.extend(fetch_all_tuscany_events(start_at))
    except Exception:
        pass
    try:
        source_events.extend(fetch_all_umbria_events(start_at))
    except Exception:
        pass
    try:
        source_events.extend(fetch_all_abruzzo_events(start_at))
    except Exception:
        pass
    for source in session.execute(select(EventSource).where(EventSource.enabled.is_(True))).scalars():
        try:
            source_events.extend(
                fetch_source_events(
                    SourceConfig(
                        name=source.name,
                        url=source.url,
                        municipality=source.municipality,
                        province=source.province or "",
                        region=source.region,
                        latitude=source.latitude,
                        longitude=source.longitude,
                    ),
                    start_at,
                )
            )
        except Exception:
            continue

    raw_payloads = source_events or _build_demo_events(start_at)
    payloads = list({payload["slug"]: payload for payload in raw_payloads}.values())

    categories: dict[str, Category] = {}
    locations: dict[tuple[str, str, str], Location] = {}
    created = 0

    for payload in payloads:
        category_name = payload["category_name"]
        category = categories.get(category_name) or _ensure_category(session, category_name)
        categories[category_name] = category

        key = (payload["municipality"], payload["province"], payload["region"])
        location = locations.get(key) or _ensure_location(
            session,
            payload["municipality"],
            payload["province"],
            payload["region"],
            payload["latitude"],
            payload["longitude"],
        )
        locations[key] = location

        event = Event(
            slug=payload["slug"],
            title=payload["title"],
            short_description=payload["short_description"],
            description=payload["description"],
            category_id=category.id,
            location_id=location.id,
            starts_at=payload["starts_at"],
            ends_at=payload["ends_at"],
            all_day=False,
            is_free=payload["is_free"],
            source_name=payload["source_name"],
            source_url=payload["source_url"],
            official_url=payload["official_url"],
            latitude=payload["latitude"],
            longitude=payload["longitude"],
            published=payload["published"],
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(event)
        created += 1

    session.commit()
    return created
