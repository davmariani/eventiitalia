"use client";

import { useEffect, useMemo, useState } from "react";
import MapIsland from "./map-island";

export type PlaceItem = {
  name: string;
  municipality: string;
  province: string;
  region: string;
  latitude: number;
  longitude: number;
  istat_code?: string;
  isCurrentLocation?: boolean;
};

export type EventItem = {
  title: string;
  type: string;
  region: string;
  location: string;
  date: string;
  dates: string[];
  image: string;
  description: string;
  latitude: number;
  longitude: number;
  color: string;
  distanceKm?: number;
  locationPrecision?: string;
  sourceUrl?: string;
  officialUrl?: string;
};

const apiBase = () => process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const getEventSourceUrl = (event: EventItem) => event.officialUrl ?? event.sourceUrl ?? `https://www.google.com/search?q=${encodeURIComponent(`${event.title} ${event.location}`)}`;
const radiusOptions = [10, 25, 50, 75, 100, 150, 200, 300, 500] as const;
const categoryOptions = ["Tutti", "Sagre", "Mercatini", "Mostre", "Concerti", "Festival", "Teatro", "Sport", "Famiglie", "Fiere"];
const categoryTypes: Record<string, string> = { Sagre: "Sagre", Mercatini: "Mercatini", Mostre: "Mostre", Concerti: "Concerti", Festival: "Festival", Teatro: "Teatro", Sport: "Sport", Famiglie: "Famiglie", Fiere: "Fiere" };
const fallbackDates = ["2026-09-26", "2026-09-27", "2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02", "2026-10-03", "2026-10-04"];
const eventsPerPage = 9;
const todayIso = () => new Date().toISOString().slice(0, 10);
const addDaysIso = (date: Date, days: number) => {
  const copy = new Date(date);
  copy.setDate(copy.getDate() + days);
  return copy.toISOString().slice(0, 10);
};
const weekendRange = () => {
  const now = new Date();
  const day = now.getDay();
  const saturdayOffset = day === 0 ? -1 : 6 - day;
  const saturday = new Date(now);
  saturday.setDate(now.getDate() + saturdayOffset);
  return { from: saturday.toISOString().slice(0, 10), to: addDaysIso(saturday, 1) };
};

const formatPlace = (place: PlaceItem) => place.isCurrentLocation ? "Posizione attuale" : `${place.municipality} (${place.province}), ${place.region}`;

const demoEvents: EventItem[] = [
  { title: "Sagra della Castagna", type: "Sagre", region: "Lazio", location: "Vallerano, VT", date: "26 settembre", dates: ["2026-09-26"], image: "image-castagna", description: "Degustazioni, mercatini e tradizioni locali.", latitude: 42.345, longitude: 12.234, color: "#d95d39" },
  { title: "Mercatino di Castel Gandolfo", type: "Mercatini", region: "Lazio", location: "Castel Gandolfo, RM", date: "27 settembre", dates: ["2026-09-27"], image: "image-mercatino", description: "Artigianato e prodotti locali sul lago.", latitude: 41.747, longitude: 12.646, color: "#e5b86e" },
  { title: "Colori d'autunno", type: "Mostre", region: "Piemonte", location: "Torino, TO", date: "30 settembre", dates: ["2026-09-30"], image: "image-mostra", description: "Una mostra dedicata ai paesaggi italiani.", latitude: 45.0703, longitude: 7.6869, color: "#4e7966" },
];

export default function EventDiscovery() {
  const [selectedDate, setSelectedDate] = useState("2026-09-26");
  const [dateFrom, setDateFrom] = useState("2026-09-26");
  const [dateTo, setDateTo] = useState("2026-09-26");
  const [selectedCategory, setSelectedCategory] = useState("Tutti");
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [events, setEvents] = useState<EventItem[]>(demoEvents);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState("Aggiornamento automatico alle 01:00");
  const [adminToken, setAdminToken] = useState("");
  const [departureQuery, setDepartureQuery] = useState("");
  const [departure, setDeparture] = useState<PlaceItem | null>(null);
  const [placeResults, setPlaceResults] = useState<PlaceItem[]>([]);
  const [radiusKm, setRadiusKm] = useState<number | "all">(() => {
    if (typeof window === "undefined") return 100;
    return Number(window.localStorage.getItem("feste-radius-km")) || 100;
  });
  const [sortMode, setSortMode] = useState("date");
  const [geoMessage, setGeoMessage] = useState("");
  const [autoSelectDeparture, setAutoSelectDeparture] = useState(false);
  const [visiblePage, setVisiblePage] = useState(1);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const date = params.get("date");
    const from = params.get("date_from");
    const to = params.get("date_to");
    const radius = params.get("radius");
    const category = params.get("categories");
    const partenza = params.get("partenza");
    if (date) {
      setSelectedDate(date);
      setDateFrom(date);
      setDateTo(date);
    }
    if (from) setDateFrom(from);
    if (to) setDateTo(to);
    if (radius === "all") setRadiusKm("all");
    else if (radius && radiusOptions.includes(Number(radius) as (typeof radiusOptions)[number])) setRadiusKm(Number(radius));
    if (category && categoryOptions.includes(category)) setSelectedCategory(category);
    if (partenza) {
      setDepartureQuery(partenza);
      setAutoSelectDeparture(true);
    }
  }, []);

  useEffect(() => {
    const handleHeroSearch = (event: Event) => {
      const query = (event as CustomEvent<{ query?: string }>).detail?.query?.trim();
      if (!query) return;
      setDeparture(null);
      setDepartureQuery(query);
      setAutoSelectDeparture(true);
      if (radiusKm === "all") setRadiusKm(100);
    };
    window.addEventListener("feste-hero-search", handleHeroSearch);
    return () => window.removeEventListener("feste-hero-search", handleHeroSearch);
  }, [radiusKm]);

  useEffect(() => {
    if (departure || departureQuery.trim().length < 2) {
      setPlaceResults([]);
      return;
    }
    const timer = window.setTimeout(() => {
      fetch(`${apiBase()}/api/locations/search?q=${encodeURIComponent(departureQuery)}`)
        .then((response) => response.ok ? response.json() : [])
        .then((data: PlaceItem[]) => setPlaceResults(data))
        .catch(() => setPlaceResults([]));
    }, 250);
    return () => window.clearTimeout(timer);
  }, [departureQuery, departure]);

  useEffect(() => {
    if (departure || departureQuery.trim().length < 2) return;
    const params = new URLSearchParams(window.location.search);
    if (!params.get("partenza")) return;
    fetch(`${apiBase()}/api/locations/search?q=${encodeURIComponent(departureQuery)}&limit=1`)
      .then((response) => response.ok ? response.json() : [])
      .then((data: PlaceItem[]) => {
        if (data[0]) {
          setDeparture(data[0]);
          setDepartureQuery(formatPlace(data[0]));
          setAutoSelectDeparture(false);
        }
      })
      .catch(() => undefined);
  }, [departureQuery, departure]);

  useEffect(() => {
    const params = new URLSearchParams();
    if (departure && !departure.isCurrentLocation) params.set("partenza", departure.istat_code || departure.municipality.toLowerCase());
    params.set("radius", departure ? String(radiusKm) : "all");
    params.set("date_from", dateFrom);
    params.set("date_to", dateTo);
    if (selectedCategory !== "Tutti") params.set("categories", selectedCategory);
    window.history.replaceState(null, "", `${window.location.pathname}?${params.toString()}${window.location.hash}`);
    if (departure && typeof radiusKm === "number") window.localStorage.setItem("feste-radius-km", String(radiusKm));
  }, [departure, radiusKm, dateFrom, dateTo, selectedCategory]);

  useEffect(() => {
    const params = new URLSearchParams();
    params.set("limit", "100");
    params.set("page_size", "100");
    params.set("sort", departure && sortMode.startsWith("distance") ? sortMode : "date");
    if (departure) {
      params.set("latitude", String(departure.latitude));
      params.set("longitude", String(departure.longitude));
      if (typeof radiusKm === "number") params.set("radius_km", String(radiusKm));
    }
    if (selectedCategory !== "Tutti") params.set("categories", categoryTypes[selectedCategory]);
    params.set("date_from", `${dateFrom}T00:00:00`);
    params.set("date_to", `${dateTo}T23:59:59`);

    setIsSearching(true);
    fetch(`${apiBase()}/api/events?${params.toString()}`)
      .then((response) => response.ok ? response.json() : Promise.reject(new Error("API non disponibile")))
      .then((data: { items?: Array<{ title: string; short_description?: string; description?: string; starts_at?: string; ends_at?: string; official_url?: string; source_url?: string; latitude?: number; longitude?: number; distance_km?: number; location_precision?: string; category_name?: string; municipality?: string; province?: string; region?: string }> }) => {
        const apiEvents = (data.items ?? []).filter((item) => item.starts_at && item.latitude != null && item.longitude != null).map((item) => {
          const start = new Date(item.starts_at as string);
          const end = item.ends_at ? new Date(item.ends_at) : start;
          const dates: string[] = [];
          for (const cursor = new Date(start); cursor <= end; cursor.setUTCDate(cursor.getUTCDate() + 1)) dates.push(cursor.toISOString().slice(0, 10));
          return {
            title: item.title,
            type: item.category_name ?? "Eventi",
            region: item.region ?? "Italia",
            location: [item.municipality, item.province].filter(Boolean).join(", "),
            date: start.toLocaleDateString("it-IT", { day: "numeric", month: "long" }),
            dates,
            image: "image-mostra",
            description: item.short_description ?? item.description ?? "Evento importato da una fonte pubblica.",
            latitude: item.latitude as number,
            longitude: item.longitude as number,
            color: "#d95d39",
            distanceKm: item.distance_km,
            locationPrecision: item.location_precision,
            sourceUrl: item.source_url,
            officialUrl: item.official_url,
          };
        });
        setEvents(apiEvents.length > 0 ? apiEvents : demoEvents);
      })
      .catch(() => setEvents(demoEvents))
      .finally(() => setIsSearching(false));
  }, [departure, radiusKm, sortMode, selectedCategory, dateFrom, dateTo]);

  const visibleEvents = useMemo(() => {
    const filtered = events.filter((event) => event.dates.some((date) => date >= dateFrom && date <= dateTo));
    if (!departure || !sortMode.startsWith("distance")) return filtered;
    return [...filtered].sort((a, b) => sortMode === "distance_desc" ? (b.distanceKm ?? -1) - (a.distanceKm ?? -1) : (a.distanceKm ?? 999999) - (b.distanceKm ?? 999999));
  }, [events, dateFrom, dateTo, departure, sortMode]);
  const pagedEvents = visibleEvents.slice(0, visiblePage * eventsPerPage);
  const hasMoreEvents = pagedEvents.length < visibleEvents.length;

  useEffect(() => {
    setVisiblePage(1);
  }, [departure, radiusKm, sortMode, selectedCategory, dateFrom, dateTo]);

  const availableDateOptions = Array.from(new Set([...fallbackDates, ...events.flatMap((event) => event.dates)])).sort().map((value) => {
    const date = new Date(`${value}T12:00:00`);
    return { value, day: date.toLocaleDateString("it-IT", { weekday: "short" }).replace(".", ""), number: date.getDate().toString(), month: date.toLocaleDateString("it-IT", { month: "short" }).replace(".", "") };
  });

  const selectPlace = (place: PlaceItem) => {
    setDeparture(place);
    setDepartureQuery(formatPlace(place));
    setPlaceResults([]);
    if (!radiusKm || radiusKm === "all") setRadiusKm(100);
    setGeoMessage("");
  };

  const setSingleDate = (value: string) => {
    setSelectedDate(value);
    setDateFrom(value);
    setDateTo(value);
  };

  useEffect(() => {
    if (!autoSelectDeparture || departure || placeResults.length === 0) return;
    selectPlace(placeResults[0]);
    setAutoSelectDeparture(false);
  }, [autoSelectDeparture, departure, placeResults]);

  const clearDeparture = () => {
    setDeparture(null);
    setDepartureQuery("");
    setPlaceResults([]);
    setGeoMessage("");
    setSortMode("date");
  };

  const useCurrentLocation = () => {
    if (!navigator.geolocation) {
      setGeoMessage("Posizione non disponibile su questo dispositivo.");
      return;
    }
    setGeoMessage("Richiesta posizione...");
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const current: PlaceItem = { name: "Posizione attuale", municipality: "Posizione attuale", province: "", region: "", latitude: position.coords.latitude, longitude: position.coords.longitude, isCurrentLocation: true };
        selectPlace(current);
        setGeoMessage("Posizione attuale selezionata.");
      },
      () => setGeoMessage("Permesso posizione negato o non disponibile."),
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 },
    );
  };

  const refreshDatabase = async () => {
    setIsRefreshing(true);
    setRefreshMessage("Aggiornamento in corso...");
    try {
      const headers: HeadersInit = {};
      if (adminToken.trim()) headers["X-Admin-Token"] = adminToken.trim();
      const response = await fetch(`${apiBase()}/api/admin/refresh-db`, { method: "POST", headers });
      const data = await response.json();
      if (!response.ok) throw new Error(data?.message ?? "Aggiornamento non riuscito");
      setRefreshMessage(`Database aggiornato: ${data.updated_events ?? 0} eventi`);
    } catch (error) {
      setRefreshMessage(error instanceof Error ? error.message : "Aggiornamento non riuscito");
    } finally {
      setIsRefreshing(false);
    }
  };

  const emptyMessage = departure && typeof radiusKm === "number" ? `Nessun evento trovato entro ${radiusKm} km da ${departure.municipality} per questa data.` : "Nessun evento trovato.";

  return (
    <section className="discover" id="scopri">
      <div className="section-heading"><div><p className="eyebrow">Scegli quando uscire</p><h2>Che giorno<br /><em>hai libero?</em></h2></div><div className="result-count"><strong>{visibleEvents.length}</strong> eventi trovati</div></div>
      <div className="geo-search">
        <label className="place-search">Partenza<input value={departureQuery} onChange={(event) => { setDepartureQuery(event.target.value); setDeparture(null); }} placeholder="Roma, Tarquinia, Milano..." /></label>
        {departure && <button className="geo-clear" type="button" onClick={clearDeparture}>Cancella</button>}
        <button className="geo-location" type="button" onClick={useCurrentLocation}>Usa la mia posizione</button>
        <label className="radius-search">Distanza massima<select disabled={!departure} value={departure ? radiusKm : "all"} onChange={(event) => setRadiusKm(event.target.value === "all" ? "all" : Number(event.target.value))}><option value="all">Tutta Italia</option>{radiusOptions.map((option) => <option value={option} key={option}>{option} km</option>)}</select></label>
        <label className="radius-search">Ordina<select value={sortMode} onChange={(event) => setSortMode(event.target.value)}><option value="date">Data</option><option value="distance_asc" disabled={!departure}>Distanza crescente</option><option value="distance_desc" disabled={!departure}>Distanza decrescente</option></select></label>
        {placeResults.length > 0 && <div className="place-results">{placeResults.map((place) => <button type="button" key={place.istat_code} onClick={() => selectPlace(place)}>{formatPlace(place)}</button>)}</div>}
      </div>
      {(geoMessage || isSearching) && <div className="selected-date-note">{isSearching ? "Ricerca in corso..." : geoMessage}</div>}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", marginBottom: "12px", flexWrap: "wrap" }}>
        <div className="selected-date-note" style={{ margin: 0 }}>{refreshMessage}</div>
        <div className="admin-refresh">
          <input aria-label="Password aggiornamento DB" type="password" value={adminToken} onChange={(event) => setAdminToken(event.target.value)} placeholder="Password admin" />
          <button type="button" onClick={refreshDatabase} disabled={isRefreshing || !adminToken.trim()}>{isRefreshing ? "Aggiornamento..." : "Aggiorna DB adesso"}</button>
        </div>
      </div>
      <div className="date-picker" aria-label="Seleziona la data degli eventi">
        <div className="date-picker-label">Eventi disponibili <span>{availableDateOptions.length > 0 ? new Date(`${availableDateOptions[0].value}T12:00:00`).getFullYear() : ""}</span></div>
        <div className="date-options">{availableDateOptions.map((date) => <button className={date.value === selectedDate && dateFrom === dateTo ? "date-option active" : "date-option"} key={date.value} onClick={() => setSingleDate(date.value)} type="button" aria-pressed={date.value === selectedDate && dateFrom === dateTo}><small>{date.day}</small><strong>{date.number}</strong><small>{date.month}</small></button>)}</div>
        <button className="calendar-button" type="button" aria-label="Apri il calendario">▦</button>
      </div>
      <div className="date-range-panel">
        <div className="date-shortcuts">
          <button type="button" onClick={() => setSingleDate(todayIso())}>Oggi</button>
          <button type="button" onClick={() => setSingleDate(addDaysIso(new Date(), 1))}>Domani</button>
          <button type="button" onClick={() => { const range = weekendRange(); setDateFrom(range.from); setDateTo(range.to); setSelectedDate(range.from); }}>Questo weekend</button>
        </div>
        <label>Dal<input type="date" value={dateFrom} onChange={(event) => { const value = event.target.value; setDateFrom(value); if (dateTo < value) setDateTo(value); setSelectedDate(value); }} /></label>
        <label>Al<input type="date" value={dateTo} onChange={(event) => setDateTo(event.target.value < dateFrom ? dateFrom : event.target.value)} /></label>
      </div>
      <div className="category-filter" aria-label="Filtra per categoria"><span className="filter-label">Tipo di evento</span>{categoryOptions.map((category) => <button className={category === selectedCategory ? "category-chip active" : "category-chip"} key={category} onClick={() => setSelectedCategory(category)} type="button" aria-pressed={category === selectedCategory}>{category}</button>)}<a className="map-filter-link" href="#mappa">Mappa <span>↘</span></a></div>
      <div className="selected-date-note">Eventi {dateFrom === dateTo ? <>per <strong>{new Date(`${dateFrom}T12:00:00`).toLocaleDateString("it-IT", { weekday: "long", day: "numeric", month: "long" })}</strong></> : <>dal <strong>{new Date(`${dateFrom}T12:00:00`).toLocaleDateString("it-IT", { day: "numeric", month: "long" })}</strong> al <strong>{new Date(`${dateTo}T12:00:00`).toLocaleDateString("it-IT", { day: "numeric", month: "long" })}</strong></>}{departure && <span> · {typeof radiusKm === "number" ? `${radiusKm} km da ${departure.municipality}` : "Tutta Italia"}</span>}</div>
      {visibleEvents.length > 0 ? <><div className="event-grid">{pagedEvents.map((event) => <article className="event-card" key={`${event.title}-${event.date}`}><div className={`event-image ${event.image}`}><span>{event.date.toUpperCase()}</span></div><div className="event-content"><p className="event-type">{event.type} · {event.region}</p><h3>{event.title}</h3><p>{event.location}</p>{departure && event.distanceKm != null && <p className="event-distance">📍 {event.distanceKm.toFixed(1)} km da {departure.municipality}, in linea d'aria</p>}<p className="event-description">{event.description}</p><button className="event-detail-button" type="button" onClick={() => setSelectedEvent(event)}>Scopri l&apos;evento <span>↗</span></button></div></article>)}</div>{hasMoreEvents && <div className="pagination-actions"><button type="button" onClick={() => setVisiblePage((page) => page + 1)}>Mostra altri 9 eventi <span>{pagedEvents.length}/{visibleEvents.length}</span></button></div>}</> : <div className="empty-results"><strong>{emptyMessage}</strong><span>{departure ? "Prova ad ampliare il raggio o cambiare data." : "Prova a cambiare data o categoria."}</span></div>}
      <div className="map-section" id="mappa"><div className="map-heading"><div><p className="eyebrow">Esplora sulla mappa</p><h2>Succede<br /><em>qui vicino.</em></h2></div><div className="map-intro"><p>Gli eventi mostrati corrispondono ai filtri attivi.</p><button type="button" onClick={useCurrentLocation}>Usa la mia posizione <span>↗</span></button></div></div><MapIsland events={pagedEvents} selectedDate={dateFrom} onEventClick={(mapEvent) => { const event = pagedEvents.find((item) => item.title === mapEvent.title); if (event) setSelectedEvent(event); }} departure={departure} radiusKm={radiusKm} /></div>
      {selectedEvent && <div className="event-modal-backdrop" role="presentation" onMouseDown={() => setSelectedEvent(null)}><article className="event-modal" role="dialog" aria-modal="true" aria-labelledby="event-modal-title" onMouseDown={(event) => event.stopPropagation()}><button className="modal-close" type="button" onClick={() => setSelectedEvent(null)} aria-label="Chiudi dettaglio evento">×</button><div className={`modal-image ${selectedEvent.image}`}><span>{selectedEvent.date.toUpperCase()}</span></div><div className="modal-content"><p className="event-type">{selectedEvent.type} · {selectedEvent.region}</p><h2 id="event-modal-title">{selectedEvent.title}</h2><p className="modal-location">{selectedEvent.location}</p>{departure && selectedEvent.distanceKm != null && <p className="event-distance">Distanza geografica: {selectedEvent.distanceKm.toFixed(1)} km da {departure.municipality}</p>}<p>{selectedEvent.description}</p><div className="modal-facts"><span><strong>Quando</strong>{selectedEvent.date}</span><span><strong>Posizione</strong>{selectedEvent.locationPrecision === "municipality" ? "Comune approssimato" : "Fonte evento"}</span></div><a className="modal-source" href={getEventSourceUrl(selectedEvent)} target="_blank" rel="noreferrer">Vai alla fonte ufficiale <span>↗</span></a></div></article></div>}
    </section>
  );
}
