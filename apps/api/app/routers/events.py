from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Event
from app.refresh import get_event_window, refresh_demo_data
from app.schemas import EventListResponse, EventSummary

router = APIRouter(prefix="/api", tags=["events"])


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


@router.get("/events", response_model=EventListResponse)
def list_events(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> EventListResponse:
    start_at, end_at = get_event_window()
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
            .limit(limit)
            .all()
        )
    except SQLAlchemyError:
        return EventListResponse(items=demo_events()[:limit], total=min(limit, len(demo_events())))

    if not items:
        fallback = demo_events()[:limit]
        return EventListResponse(items=fallback, total=len(fallback))

    mapped = [
        EventSummary(
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
            published=item.published,
            category_name=item.category.name if item.category else None,
            municipality=item.location.municipality if item.location else None,
            province=item.location.province if item.location else None,
            region=item.location.region if item.location else None,
        )
        for item in items
    ]

    return EventListResponse(items=mapped, total=len(mapped))
