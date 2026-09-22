from __future__ import annotations

import html
import re
from calendar import monthrange
from datetime import datetime, timedelta, timezone
from urllib.parse import urljoin

import httpx


CALENDAR_URL = "https://comune.viterbo.it/vivere-il-comune/eventi/"
BASE_URL = "https://comune.viterbo.it"
ITALIAN_MONTHS = {
    "gennaio": 1,
    "febbraio": 2,
    "marzo": 3,
    "aprile": 4,
    "maggio": 5,
    "giugno": 6,
    "luglio": 7,
    "agosto": 8,
    "settembre": 9,
    "ottobre": 10,
    "novembre": 11,
    "dicembre": 12,
}
DATE_PATTERN = re.compile(
    r"(?:dal\s+)?(?P<day>\d{1,2})(?:\s*(?:al|[-–])\s*(?P<end_day>\d{1,2}))?\s+(?P<month>gennaio|febbraio|marzo|aprile|maggio|giugno|luglio|agosto|settembre|ottobre|novembre|dicembre)",
    re.IGNORECASE,
)


def _clean_text(value: str) -> str:
    value = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", value, flags=re.IGNORECASE | re.DOTALL)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _first_match(pattern: str, value: str) -> str | None:
    match = re.search(pattern, value, re.IGNORECASE | re.DOTALL)
    return _clean_text(match.group(1)) if match else None


def _parse_dates(text: str, reference_now: datetime) -> tuple[datetime, datetime] | None:
    match = DATE_PATTERN.search(text)
    if not match:
        return None

    month = ITALIAN_MONTHS[match.group("month").lower()]
    year = reference_now.year
    if month < reference_now.month - 6:
        year += 1
    day = int(match.group("day"))
    end_day = int(match.group("end_day") or day)
    try:
        start = datetime(year, month, day, 12, tzinfo=timezone.utc)
        end = datetime(year, month, end_day, 23, 59, tzinfo=timezone.utc)
    except ValueError:
        return None

    if end < start:
        end = start + timedelta(hours=2)
    return start, end


def _extract_event_links(calendar_html: str) -> list[str]:
    links = re.findall(r'href=["\']([^"\']+/vivere-il-comune/eventi/[^"\']+/?)', calendar_html, re.IGNORECASE)
    return list(dict.fromkeys(urljoin(BASE_URL, html.unescape(link)) for link in links))


def _parse_event_page(page_html: str, url: str, reference_now: datetime) -> dict | None:
    title = _first_match(r"<h1[^>]*>(.*?)</h1>", page_html) or _first_match(r"<title[^>]*>(.*?)</title>", page_html)
    if not title:
        return None

    title = re.sub(r"\s+[–-]\s+Comune di Viterbo$", "", title).strip()
    content = _clean_text(page_html)
    dates = _parse_dates(content, reference_now)
    if not dates:
        return None

    start, end = dates
    description = content[:1000]
    return {
        "slug": url.rstrip("/").rsplit("/", 1)[-1],
        "title": title,
        "short_description": description[:300],
        "description": description,
        "starts_at": start,
        "ends_at": end,
        "all_day": True,
        "is_free": True,
        "source_name": "Comune di Viterbo",
        "source_url": url,
        "official_url": url,
        "latitude": 42.4174,
        "longitude": 12.1084,
        "published": True,
        "category_name": "Eventi",
        "municipality": "Viterbo",
        "province": "VT",
        "region": "Lazio",
    }


def fetch_comune_viterbo_events(reference_now: datetime | None = None) -> list[dict]:
    now = (reference_now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    window_end = now + timedelta(days=90)
    with httpx.Client(timeout=20, follow_redirects=True, headers={"User-Agent": "FesteItalia/0.1 event importer"}) as client:
        calendar_response = client.get(CALENDAR_URL)
        calendar_response.raise_for_status()
        events_by_title: dict[str, dict] = {}
        for url in _extract_event_links(calendar_response.text):
            try:
                page_response = client.get(url)
                page_response.raise_for_status()
                event = _parse_event_page(page_response.text, url, now)
            except (httpx.HTTPError, ValueError):
                continue
            if event and event["ends_at"] >= now and event["starts_at"] <= window_end:
                key = re.sub(r"\s+", " ", event["title"].lower()).strip()
                current = events_by_title.get(key)
                if current is None or event["starts_at"] < current["starts_at"]:
                    events_by_title[key] = event
    return sorted(events_by_title.values(), key=lambda event: event["starts_at"])