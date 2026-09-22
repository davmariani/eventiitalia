from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin, urlparse

import httpx

from app.sources.comune_viterbo import ITALIAN_MONTHS, DATE_PATTERN


@dataclass(frozen=True)
class SourceConfig:
    name: str
    url: str
    municipality: str | None = None
    province: str = "VT"
    region: str = "Lazio"
    latitude: float | None = None
    longitude: float | None = None


SOURCES = [
    SourceConfig("Provincia di Viterbo", "https://www.provincia.viterbo.it/home/245-notizie_dallarea_vasta/625-eventi_folkloristici_culturali_religiosi_enogastronomici.html"),
    SourceConfig("Tuscia Welcome", "https://www.tusciawelcome.it/it/"),
    SourceConfig("Comune di Tarquinia", "https://www.comune.tarquinia.vt.it/", "Tarquinia", latitude=42.254, longitude=11.756),
    SourceConfig("Comune di Civita Castellana", "https://www.comune.civitacastellana.vt.it/", "Civita Castellana", latitude=42.296, longitude=12.407),
    SourceConfig("Comune di Orte", "https://www.comune.orte.vt.it/", "Orte", latitude=42.460, longitude=12.386),
    SourceConfig("Comune di Montefiascone", "https://www.comune.montefiascone.vt.it/", "Montefiascone", latitude=42.540, longitude=12.034),
    SourceConfig("Comune di Bolsena", "https://www.comunebolsena.it/", "Bolsena", latitude=42.645, longitude=11.986),
    SourceConfig("Comune di Caprarola", "https://www.comune.caprarola.vt.it/", "Caprarola", latitude=42.325, longitude=12.237),
    SourceConfig("Comune di Ronciglione", "https://www.comune.ronciglione.vt.it/", "Ronciglione", latitude=42.291, longitude=12.215),
    SourceConfig("Comune di Tuscania", "https://www.comune.tuscania.vt.it/", "Tuscania", latitude=42.420, longitude=11.870),
    SourceConfig("Comune di Acquapendente", "https://www.comune.acquapendente.vt.it/", "Acquapendente", latitude=42.745, longitude=11.866),
]


def _clean_text(value: str) -> str:
    value = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _parse_dates(text: str, reference_now: datetime) -> tuple[datetime, datetime] | None:
    match = DATE_PATTERN.search(text)
    if not match:
        return None
    month = ITALIAN_MONTHS[match.group("month").lower()]
    year = reference_now.year + (1 if month < reference_now.month - 6 else 0)
    day = int(match.group("day"))
    end_day = int(match.group("end_day") or day)
    try:
        start = datetime(year, month, day, 12, tzinfo=timezone.utc)
        end = datetime(year, month, end_day, 23, 59, tzinfo=timezone.utc)
    except ValueError:
        return None
    return start, end if end >= start else start + timedelta(hours=2)


def _event_links(source: SourceConfig, page: str) -> list[str]:
    host = urlparse(source.url).netloc
    candidates = re.findall(r'href=["\']([^"\']+)["\']', page, re.IGNORECASE)
    links: list[str] = []
    for candidate in candidates:
        url = urljoin(source.url, html.unescape(candidate)).split("#", 1)[0]
        parsed = urlparse(url)
        path = parsed.path.lower()
        if parsed.netloc != host or url.rstrip("/") == source.url.rstrip("/"):
            continue
        if any(token in path for token in ("event", "manifest", "sagra", "festa", "calendario", "folclore")):
            links.append(url)
    return list(dict.fromkeys(links))[:80]


def _parse_event(source: SourceConfig, url: str, page: str, now: datetime) -> dict | None:
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>|<title[^>]*>(.*?)</title>", page, re.IGNORECASE | re.DOTALL)
    if not title_match:
        return None
    title = _clean_text(title_match.group(1) or title_match.group(2) or "")
    title = re.sub(r"\s+[–-]\s+(.+?)(?:Comune|Provincia).*$", "", title, flags=re.IGNORECASE).strip()
    content = _clean_text(page)
    dates = _parse_dates(content, now)
    if not title or not dates:
        return None
    start, end = dates
    return {
        "slug": re.sub(r"[^a-z0-9]+", "-", url.rstrip("/").rsplit("/", 1)[-1].lower()).strip("-")[:210],
        "title": title[:220],
        "short_description": content[:300],
        "description": content[:1000],
        "starts_at": start,
        "ends_at": end,
        "all_day": True,
        "is_free": True,
        "source_name": source.name,
        "source_url": url,
        "official_url": url,
        "latitude": source.latitude,
        "longitude": source.longitude,
        "published": True,
        "category_name": "Eventi",
        "municipality": source.municipality or "Viterbo",
        "province": source.province,
        "region": source.region,
    }


def fetch_source_events(source: SourceConfig, reference_now: datetime | None = None) -> list[dict]:
    now = (reference_now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    window_end = now + timedelta(days=90)
    with httpx.Client(timeout=15, follow_redirects=True, headers={"User-Agent": "FesteItalia/0.1 event importer"}) as client:
        response = client.get(source.url)
        response.raise_for_status()
        links = _event_links(source, response.text)
        events_by_slug: dict[str, dict] = {}
        for url in links:
            try:
                detail = client.get(url)
                detail.raise_for_status()
                event = _parse_event(source, url, detail.text, now)
            except (httpx.HTTPError, ValueError):
                continue
            if event and event["ends_at"] >= now and event["starts_at"] <= window_end:
                events_by_slug[event["slug"]] = event
    return sorted(events_by_slug.values(), key=lambda event: event["starts_at"])


def fetch_all_tuscia_events(reference_now: datetime | None = None) -> list[dict]:
    events: list[dict] = []
    for source in SOURCES:
        try:
            events.extend(fetch_source_events(source, reference_now))
        except (httpx.HTTPError, ValueError):
            continue
    return list({event["slug"]: event for event in events}.values())