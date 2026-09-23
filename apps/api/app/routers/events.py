import math
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.geo_places import search_places
from app.models import Event, EventSource
from app.refresh import get_event_window, refresh_demo_data
from app.schemas import EventListResponse, EventSourceCreate, EventSourceSummary, EventSummary, GeoPlaceSummary

router = APIRouter(prefix="/api", tags=["events"])
ALLOWED_RADII_KM = {10, 25, 50, 75, 100, 150, 200, 300, 500}


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0088
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    return earth_radius_km * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def map_event(item: Event, distance_km: float | None = None) -> EventSummary:
    location_precision = None
    if item.latitude is not None and item.longitude is not None:
        location_precision = "municipality" if item.location else "source"
    return EventSummary(
        id=item.id,
        slug=item.slug,
        title=item.title,
        short_description=item.short_description,
        description=item.description,
        starts_at=item.starts_at,
        ends_at=item.ends_at,
        is_free=item.is_free,
        price_min=item.price_min,
        price_max=item.price_max,
        source_name=item.source_name,
        source_url=item.source_url,
        official_url=item.official_url,
        latitude=item.latitude,
        longitude=item.longitude,
        distance_km=round(distance_km, 1) if distance_km is not None else None,
        location_precision=location_precision,
        published=item.published,
        category_name=item.category.name if item.category else None,
        municipality=item.location.municipality if item.location else None,
        province=item.location.province if item.location else None,
        region=item.location.region if item.location else None,
    )


def demo_events() -> list[EventSummary]:
    start_at, end_at = get_event_window()
    items = [
        EventSummary(
            id=1,
            slug="sagra-della-castagna-vallerano",
            title="Sagra della Castagna",
            short_description="Manifestazione enogastronomica con degustazioni e mercatini.",
            description="Evento dedicato alla castagna e alle tradizioni locali.",
            starts_at=(start_at + timedelta(days=0, hours=10)).isoformat(),
            ends_at=(start_at + timedelta(days=0, hours=20)).isoformat(),
            is_free=True,
            source_name="Comune di Vallerano",
            source_url="https://example.com/fonte",
            official_url="https://example.com/evento",
            latitude=42.345,
            longitude=12.234,
            distance_km=None,
            location_precision="municipality",
            published=True,
            category_name="Sagre",
            municipality="Vallerano",
            province="VT",
            region="Lazio",
        ),
        EventSummary(
            id=2,
            slug="mercatino-di-castel-gandolfo",
            title="Mercatino di Castel Gandolfo",
            short_description="Passeggiata, artigianato e prodotti locali.",
            description="Mercatino con bancarelle e prodotti tipici del territorio.",
            starts_at=(start_at + timedelta(days=2, hours=9)).isoformat(),
            ends_at=(start_at + timedelta(days=2, hours=19)).isoformat(),
            is_free=True,
            source_name="Comune di Castel Gandolfo",
            source_url="https://example.com/fonte-2",
            official_url="https://example.com/evento-2",
            latitude=41.747,
            longitude=12.646,
            distance_km=None,
            location_precision="municipality",
            published=True,
            category_name="Mercatini",
            municipality="Castel Gandolfo",
            province="RM",
            region="Lazio",
        ),
    ]
    return items


@router.post("/admin/refresh-db")
def refresh_db(db: Session = Depends(get_db)) -> dict:
    try:
        count = refresh_demo_data(db)
        return {
            "status": "ok",
            "message": "Database aggiornato correttamente.",
            "updated_events": count,
            "schedule": "ogni giorno alle 01:00",
        }
    except SQLAlchemyError as exc:
        return {
            "status": "error",
            "message": str(exc),
            "updated_events": 0,
            "schedule": "ogni giorno alle 01:00",
        }


@router.get("/admin/sources", response_model=list[EventSourceSummary])
def list_sources(db: Session = Depends(get_db)) -> list[EventSource]:
    return db.query(EventSource).order_by(EventSource.created_at.desc()).all()


@router.post("/admin/sources", response_model=EventSourceSummary)
def create_source(payload: EventSourceCreate, db: Session = Depends(get_db)) -> EventSource:
    source = EventSource(
        name=payload.name.strip(),
        url=str(payload.url).strip(),
        municipality=payload.municipality.strip() if payload.municipality else None,
        province=payload.province.strip().upper() if payload.province else None,
        region=payload.region.strip() or "Italia",
        latitude=payload.latitude,
        longitude=payload.longitude,
        enabled=True,
    )
    if not source.name or not source.url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Nome e URL pubblico sono obbligatori.")
    db.add(source)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Questa fonte esiste già.") from exc
    db.refresh(source)
    return source


@router.get("/locations/search", response_model=list[GeoPlaceSummary])
def search_locations(q: str = Query(..., min_length=2), limit: int = Query(8, ge=1, le=20)) -> list[GeoPlaceSummary]:
    return [
        GeoPlaceSummary(
            name=place.name,
            municipality=place.municipality,
            province=place.province,
            region=place.region,
            latitude=place.latitude,
            longitude=place.longitude,
            istat_code=place.istat_code,
        )
        for place in search_places(q, limit)
    ]


@router.get("/events", response_model=EventListResponse)
def list_events(
    limit: int = Query(20, ge=1, le=100),
    latitude: float | None = Query(None, ge=-90, le=90),
    longitude: float | None = Query(None, ge=-180, le=180),
    radius_km: int | None = Query(None),
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    categories: str | None = None,
    sort: str = Query("date", pattern="^(date|distance_asc|distance_desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
) -> EventListResponse:
    if (latitude is None) != (longitude is None):
        raise HTTPException(status_code=400, detail="Latitudine e longitudine devono essere inviate insieme.")
    if radius_km is not None and radius_km not in ALLOWED_RADII_KM:
        raise HTTPException(status_code=400, detail="Raggio non consentito.")
    if sort.startswith("distance") and (latitude is None or longitude is None):
        raise HTTPException(status_code=400, detail="Ordinamento per distanza disponibile solo con una località.")

    start_at, end_at = get_event_window()
    if date_from:
        start_at = date_from
    if date_to:
        end_at = date_to
    requested_categories = {item.strip().casefold() for item in categories.split(",")} if categories else set()
    try:
        items = (
            db.query(Event)
            .filter(
                and_(
                    Event.starts_at.is_not(None),
                    Event.starts_at >= start_at,
                    Event.starts_at <= end_at,
                )
            )
            .order_by(Event.starts_at.asc())
            .limit(max(limit, page * page_size))
            .all()
        )
    except SQLAlchemyError:
        return EventListResponse(items=demo_events()[:limit], total=min(limit, len(demo_events())))

    if not items:
        fallback = demo_events()[:limit]
        return EventListResponse(items=fallback, total=len(fallback))

    filtered: list[tuple[Event, float | None]] = []
    for item in items:
        category_name = item.category.name if item.category else None
        if requested_categories and (category_name or "").casefold() not in requested_categories:
            continue
        distance = None
        if latitude is not None and longitude is not None:
            if item.latitude is None or item.longitude is None:
                continue
            distance = haversine_km(latitude, longitude, item.latitude, item.longitude)
            if radius_km is not None and distance > radius_km:
                continue
        filtered.append((item, distance))

    category_counts: dict[str, int] = {}
    for item, _distance in filtered:
        name = item.category.name if item.category else "Evento"
        category_counts[name] = category_counts.get(name, 0) + 1

    if sort == "distance_asc":
        filtered.sort(key=lambda pair: pair[1] if pair[1] is not None else float("inf"))
    elif sort == "distance_desc":
        filtered.sort(key=lambda pair: pair[1] if pair[1] is not None else -1, reverse=True)
    else:
        filtered.sort(key=lambda pair: pair[0].starts_at or datetime.max.replace(tzinfo=timezone.utc))

    start = (page - 1) * page_size
    end = start + page_size
    mapped = [map_event(item, distance) for item, distance in filtered[start:end]]

    return EventListResponse(items=mapped, total=len(filtered), category_counts=category_counts)
