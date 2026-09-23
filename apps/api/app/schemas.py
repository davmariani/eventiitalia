from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EventBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    short_description: str | None = None
    description: str | None = None
    starts_at: datetime | None = None
    ends_at: datetime | None = None
    is_free: bool = True
    price_min: float | None = None
    price_max: float | None = None
    source_name: str | None = None
    source_url: str | None = None
    official_url: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    published: bool = False


class EventSummary(EventBase):
    category_name: str | None = None
    municipality: str | None = None
    province: str | None = None
    region: str | None = None


class EventListResponse(BaseModel):
    items: list[EventSummary]
    total: int


class EventSourceCreate(BaseModel):
    name: str
    url: str
    municipality: str | None = None
    province: str | None = None
    region: str = "Italia"
    latitude: float | None = None
    longitude: float | None = None


class EventSourceSummary(EventSourceCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    enabled: bool = True
