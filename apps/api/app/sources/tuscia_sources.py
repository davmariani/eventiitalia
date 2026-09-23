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
    SourceConfig("VisitLazio", "https://www.visitlazio.com/eventi/", province="RM", region="Lazio"),
    SourceConfig("Roma Capitale", "https://www.comune.roma.it/web/it/eventi.page", "Roma", province="RM", latitude=41.9028, longitude=12.4964),
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

TUSCANY_SOURCES = [
    SourceConfig("VisitTuscany", "https://www.visittuscany.com/it/eventi/", province="FI", region="Toscana"),
    SourceConfig("Comune di Firenze", "https://www.comune.firenze.it/eventi", "Firenze", province="FI", region="Toscana", latitude=43.7696, longitude=11.2558),
    SourceConfig("Comune di Siena", "https://www.comune.siena.it/novita/eventi", "Siena", province="SI", region="Toscana", latitude=43.3188, longitude=11.3308),
    SourceConfig("Comune di Pisa", "https://www.comune.pisa.it/eventi", "Pisa", province="PI", region="Toscana", latitude=43.7228, longitude=10.4017),
    SourceConfig("Comune di Lucca", "https://www.comune.lucca.it/eventi", "Lucca", province="LU", region="Toscana", latitude=43.843, longitude=10.507),
    SourceConfig("Comune di Arezzo", "https://www.comune.arezzo.it/eventi", "Arezzo", province="AR", region="Toscana", latitude=43.4633, longitude=11.8796),
    SourceConfig("Comune di Livorno", "https://www.comune.livorno.it/eventi", "Livorno", province="LI", region="Toscana", latitude=43.5485, longitude=10.3106),
    SourceConfig("Comune di Grosseto", "https://www.comune.grosseto.it/eventi", "Grosseto", province="GR", region="Toscana", latitude=42.7635, longitude=11.1124),
    SourceConfig("Comune di Pistoia", "https://www.comune.pistoia.it/eventi", "Pistoia", province="PT", region="Toscana", latitude=43.933, longitude=10.917),
    SourceConfig("Comune di Prato", "https://www.comune.prato.it/eventi", "Prato", province="PO", region="Toscana", latitude=43.8777, longitude=11.1022),
    SourceConfig("Comune di Massa", "https://www.comune.massa.ms.it/eventi", "Massa", province="MS", region="Toscana", latitude=44.035, longitude=10.14),
]

TUSCANY_PROVINCE_SOURCES = [
    SourceConfig("Provincia di Firenze", "https://www.provincia.fi.it/", province="FI", region="Toscana", latitude=43.7696, longitude=11.2558),
    SourceConfig("Provincia di Siena", "https://www.provincia.siena.it/la-provincia/eventi/", province="SI", region="Toscana", latitude=43.3188, longitude=11.3308),
    SourceConfig("Provincia di Pisa", "https://www.provincia.pisa.it/", province="PI", region="Toscana", latitude=43.7228, longitude=10.4017),
    SourceConfig("Provincia di Lucca", "https://www.provincia.lucca.it/tema-provincia/eventi-e-beni-culturali-biblioteche", province="LU", region="Toscana", latitude=43.843, longitude=10.507),
    SourceConfig("Provincia di Arezzo", "https://provincia.arezzo.it/novita/notizie/", province="AR", region="Toscana", latitude=43.4633, longitude=11.8796),
    SourceConfig("Provincia di Livorno", "https://www.provincia.livorno.it/", province="LI", region="Toscana", latitude=43.5485, longitude=10.3106),
    SourceConfig("Provincia di Grosseto", "https://www.provincia.grosseto.it/", province="GR", region="Toscana", latitude=42.7635, longitude=11.1124),
    SourceConfig("Provincia di Pistoia", "https://www.provincia.pistoia.it/", province="PT", region="Toscana", latitude=43.933, longitude=10.917),
    SourceConfig("Provincia di Prato", "https://www.provincia.prato.it/", province="PO", region="Toscana", latitude=43.8777, longitude=11.1022),
    SourceConfig("Provincia di Massa-Carrara", "https://www.provincia.ms.it/", province="MS", region="Toscana", latitude=44.035, longitude=10.14),
]

LAZIO_PROVINCE_SOURCES = [
    SourceConfig("Città Metropolitana di Roma Capitale", "https://www.cittametropolitana.roma.it/", province="RM", region="Lazio", latitude=41.9028, longitude=12.4964),
    SourceConfig("Provincia di Frosinone", "https://www.provincia.frosinone.it/", province="FR", region="Lazio", latitude=41.6396, longitude=13.3516),
    SourceConfig("Provincia di Latina", "https://www.provincia.latina.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/14027", province="LT", region="Lazio", latitude=41.4676, longitude=12.9037),
    SourceConfig("Provincia di Rieti", "https://www.provincia.rieti.it/", province="RI", region="Lazio", latitude=42.4049, longitude=12.8625),
    SourceConfig("Provincia di Viterbo", "https://www.provincia.viterbo.it/home/245-notizie_dallarea_vasta/625-eventi_folkloristici_culturali_religiosi_enogastronomici.html", province="VT", region="Lazio", latitude=42.4174, longitude=12.1084),
]

UMBRIA_PROVINCE_SOURCES = [
    SourceConfig("Umbriatourism", "https://www.umbriatourism.it/it/eventi", province="PG", region="Umbria", latitude=43.1107, longitude=12.3908),
    SourceConfig("UmbriaEventi", "https://www.umbriaeventi.com/", province="PG", region="Umbria", latitude=43.1107, longitude=12.3908),
    SourceConfig("Provincia di Perugia", "https://www.provincia.perugia.it/", province="PG", region="Umbria", latitude=43.1107, longitude=12.3908),
    SourceConfig("Provincia di Terni", "https://www.provincia.terni.it/portal/comunicati-stampa", province="TR", region="Umbria", latitude=42.5636, longitude=12.6427),
]

ABRUZZO_PROVINCE_SOURCES = [
    SourceConfig("Provincia dell'Aquila", "https://www.provincia.laquila.it/", province="AQ", region="Abruzzo", latitude=42.3498, longitude=13.3995),
    SourceConfig("Provincia di Chieti", "https://www.provincia.chieti.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/466", province="CH", region="Abruzzo", latitude=42.3512, longitude=14.1676),
    SourceConfig("Provincia di Pescara", "https://www.provincia.pescara.it/it/news-category/151265", province="PE", region="Abruzzo", latitude=42.4618, longitude=14.2161),
    SourceConfig("Provincia di Teramo", "https://provincia.teramo.it/vivere-la-provincia/eventi/", province="TE", region="Abruzzo", latitude=42.6589, longitude=13.7044),
]

PROVINCE_CODES = {
    "RM": "Roma",
    "VT": "Viterbo",
    "FR": "Frosinone",
    "LT": "Latina",
    "RI": "Rieti",
}

MONTH_ALIASES = {
    **ITALIAN_MONTHS,
    "gen": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "mag": 5,
    "giu": 6,
    "lug": 7,
    "ago": 8,
    "set": 9,
    "sett": 9,
    "ott": 10,
    "nov": 11,
    "dic": 12,
}
MONTH_TOKEN_PATTERN = "|".join(sorted(MONTH_ALIASES, key=len, reverse=True))
DATE_TOKEN_PATTERN = re.compile(rf"(?P<day>\d{{1,2}})\s+(?P<month>{MONTH_TOKEN_PATTERN})(?:\s+(?P<year>\d{{4}}))?", re.IGNORECASE)
NUMERIC_DATE_PATTERN = re.compile(r"(?P<day>\d{1,2})/(?P<month>\d{1,2})/(?P<year>\d{4})")


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


def _date_from_token(match: re.Match[str], reference_now: datetime) -> datetime | None:
    month = MONTH_ALIASES.get(match.group("month").lower())
    if not month:
        return None
    year = int(match.group("year") or reference_now.year)
    if not match.group("year") and month < reference_now.month - 6:
        year += 1
    try:
        return datetime(year, month, int(match.group("day")), 12, tzinfo=timezone.utc)
    except ValueError:
        return None


def _date_from_numeric_token(match: re.Match[str]) -> datetime | None:
    try:
        return datetime(
            int(match.group("year")),
            int(match.group("month")),
            int(match.group("day")),
            12,
            tzinfo=timezone.utc,
        )
    except ValueError:
        return None


def _slug_from_title(title: str, url: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        slug = url.rstrip("/").rsplit("/", 1)[-1].lower()
    return re.sub(r"[^a-z0-9]+", "-", slug).strip("-")[:210]


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
        last_segment = path.rstrip("/").rsplit("/", 1)[-1]
        if last_segment in {"eventi", "evento", "manifestazioni", "calendario"}:
            continue
        if any(token in path for token in ("event", "manifest", "sagra", "festa", "calendario", "folclore")):
            links.append(url)
    return list(dict.fromkeys(links))[:80]


def _parse_listing_events(source: SourceConfig, page: str, now: datetime) -> list[dict]:
    events: list[dict] = []
    anchors = re.findall(r"<a\b[^>]*href=[\"']([^\"']+)[\"'][^>]*>(.*?)</a>", page, re.IGNORECASE | re.DOTALL)
    for href, raw_label in anchors:
        label = _clean_text(raw_label)
        date_matches = list(DATE_TOKEN_PATTERN.finditer(label))
        date_matches.extend(NUMERIC_DATE_PATTERN.finditer(label))
        date_matches.sort(key=lambda match: match.start())
        if not date_matches:
            continue

        start = _date_from_numeric_token(date_matches[0]) if "/" in date_matches[0].group(0) else _date_from_token(date_matches[0], now)
        end = None
        if len(date_matches) > 1:
            end = _date_from_numeric_token(date_matches[1]) if "/" in date_matches[1].group(0) else _date_from_token(date_matches[1], now)
        if not start:
            continue
        if not end or end < start:
            end = start.replace(hour=23, minute=59)
        else:
            end = end.replace(hour=23, minute=59)

        before_date = label[:date_matches[0].start()].strip(" -–|")
        after_date = label[date_matches[-1].end():].strip(" -–|")
        title = before_date if len(before_date) >= 4 else after_date
        location_match = re.search(r"([A-ZÀ-Ü][A-Za-zÀ-ÿ' -]{2,})\s*\(([A-Z]{2})\)", after_date)
        municipality = source.municipality or PROVINCE_CODES.get(source.province, source.region)
        province = source.province
        if location_match:
            municipality = location_match.group(1).strip()
            province = location_match.group(2).strip()
            if title == after_date:
                title = after_date[:location_match.start()].strip(" -–|") or title
        if not title or len(title) < 4:
            continue
        if _is_index_or_navigation_page(source, urljoin(source.url, html.unescape(href)), title, label):
            continue

        url = urljoin(source.url, html.unescape(href)).split("#", 1)[0]
        events.append(
            {
                "slug": _slug_from_title(f"{title}-{source.name}", url),
                "title": title[:220],
                "short_description": label[:300],
                "description": label[:1000],
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
                "municipality": municipality,
                "province": province,
                "region": source.region,
            }
        )
    return events


def _is_index_or_navigation_page(source: SourceConfig, url: str, title: str, content: str) -> bool:
    normalized_title = re.sub(r"\s+", " ", title).casefold().strip()
    source_name = source.name.casefold()
    path = urlparse(url).path.lower().rstrip("/")
    last_segment = path.rsplit("/", 1)[-1]

    generic_titles = {
        "eventi",
        "manifestazioni",
        "calendario eventi",
        "provincia di teramo",
    }
    if normalized_title in generic_titles or normalized_title == source_name:
        return True
    if normalized_title.startswith("eventi ") and source_name in normalized_title:
        return True
    if last_segment in {"eventi", "evento", "manifestazioni", "calendario"}:
        return True

    navigation_markers = (
        "0 eventi trovati",
        "nessun altro risultato",
        "come valuti questo servizio",
        "note legali dichiarazione di accessibilità cookie policy",
        "vai ai contenuti vai al footer",
    )
    marker_count = sum(1 for marker in navigation_markers if marker in content.casefold())
    return marker_count >= 2


def _parse_event(source: SourceConfig, url: str, page: str, now: datetime) -> dict | None:
    title_match = re.search(r"<h1[^>]*>(.*?)</h1>|<title[^>]*>(.*?)</title>", page, re.IGNORECASE | re.DOTALL)
    if not title_match:
        return None
    title = _clean_text(title_match.group(1) or title_match.group(2) or "")
    title = re.sub(r"\s+[–-]\s+(.+?)(?:Comune|Provincia).*$", "", title, flags=re.IGNORECASE).strip()
    content = _clean_text(page)
    if _is_index_or_navigation_page(source, url, title, content):
        return None
    dates = _parse_dates(content, now)
    if not title or not dates:
        return None
    start, end = dates
    municipality = source.municipality or "Lazio"
    province = source.province
    location_match = re.search(r"([A-ZÀ-Ü][A-Za-zÀ-ÿ' -]{2,})\s*\(([A-Z]{2})\)", content)
    if location_match:
        municipality = location_match.group(1).strip()
        province = location_match.group(2)
    region = source.region
    if municipality == "Lazio":
        municipality = PROVINCE_CODES.get(province, "Roma")
    return {
        "slug": _slug_from_title(title, url),
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
        "municipality": municipality,
        "province": province,
        "region": region,
    }


def fetch_source_events(source: SourceConfig, reference_now: datetime | None = None) -> list[dict]:
    now = (reference_now or datetime.now(timezone.utc)).astimezone(timezone.utc)
    window_end = now + timedelta(days=90)
    with httpx.Client(timeout=15, follow_redirects=True, headers={"User-Agent": "FesteItalia/0.1 event importer"}) as client:
        response = client.get(source.url)
        response.raise_for_status()
        events_by_slug: dict[str, dict] = {}
        for event in _parse_listing_events(source, response.text, now):
            if event["ends_at"] >= now and event["starts_at"] <= window_end:
                events_by_slug[event["slug"]] = event
        links = _event_links(source, response.text)
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
    for source in [*SOURCES, *LAZIO_PROVINCE_SOURCES]:
        try:
            events.extend(fetch_source_events(source, reference_now))
        except (httpx.HTTPError, ValueError):
            continue
    return list({event["slug"]: event for event in events}.values())


def fetch_all_tuscany_events(reference_now: datetime | None = None) -> list[dict]:
    events: list[dict] = []
    for source in [*TUSCANY_SOURCES, *TUSCANY_PROVINCE_SOURCES]:
        try:
            events.extend(fetch_source_events(source, reference_now))
        except (httpx.HTTPError, ValueError):
            continue
    return list({event["slug"]: event for event in events}.values())


def fetch_all_umbria_events(reference_now: datetime | None = None) -> list[dict]:
    events: list[dict] = []
    for source in UMBRIA_PROVINCE_SOURCES:
        try:
            events.extend(fetch_source_events(source, reference_now))
        except (httpx.HTTPError, ValueError):
            continue
    return list({event["slug"]: event for event in events}.values())


def fetch_all_abruzzo_events(reference_now: datetime | None = None) -> list[dict]:
    events: list[dict] = []
    for source in ABRUZZO_PROVINCE_SOURCES:
        try:
            events.extend(fetch_source_events(source, reference_now))
        except (httpx.HTTPError, ValueError):
            continue
    return list({event["slug"]: event for event in events}.values())
