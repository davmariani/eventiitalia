"use client";

import { useEffect, useState } from "react";
import MapIsland from "./map-island";

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
  sourceUrl?: string;
  officialUrl?: string;
};

const getEventSourceUrl = (event: EventItem) => event.officialUrl ?? event.sourceUrl ?? `https://www.google.com/search?q=${encodeURIComponent(`${event.title} ${event.location}`)}`;

const demoEvents: EventItem[] = [
  { title: "Sagra della Castagna", type: "Sagra", region: "Lazio", location: "Vallerano, VT · 42 km da te", date: "26-27 settembre", dates: ["2026-09-26", "2026-09-27"], image: "image-castagna", description: "Degustazioni, mercatini e tradizioni locali.", latitude: 42.345, longitude: 12.234, color: "#d95d39" },
  { title: "Mercatino di Castel Gandolfo", type: "Mercatino", region: "Lazio", location: "Castel Gandolfo, RM", date: "27 settembre", dates: ["2026-09-27"], image: "image-mercatino", description: "Artigianato e prodotti locali sul lago.", latitude: 41.747, longitude: 12.646, color: "#e5b86e" },
  { title: "Colori d'autunno", type: "Mostra", region: "Piemonte", location: "Torino, TO", date: "Fino al 30 settembre", dates: ["2026-09-26", "2026-09-27", "2026-09-28", "2026-09-29", "2026-09-30"], image: "image-mostra", description: "Una mostra dedicata ai paesaggi italiani.", latitude: 45.0703, longitude: 7.6869, color: "#4e7966" },
  { title: "Festival delle Colline", type: "Festival", region: "Toscana", location: "Firenze, FI", date: "26 settembre", dates: ["2026-09-26"], image: "image-mostra", description: "Musica, incontri e sapori tra le colline toscane.", latitude: 43.7696, longitude: 11.2558, color: "#4e7966" },
  { title: "Concerto al Castello", type: "Concerto", region: "Lombardia", location: "Sirmione, BS", date: "26 settembre", dates: ["2026-09-26"], image: "image-mercatino", description: "Una serata di musica dal vivo in riva al lago.", latitude: 45.4928, longitude: 10.6093, color: "#d95d39" },
  { title: "Fiera del Tartufo", type: "Fiera", region: "Piemonte", location: "Alba, CN", date: "27 settembre", dates: ["2026-09-27"], image: "image-castagna", description: "Profumi, produttori e specialità delle Langhe.", latitude: 44.7009, longitude: 8.035, color: "#e5b86e" },
  { title: "Domenica al Museo", type: "Famiglie", region: "Emilia-Romagna", location: "Bologna, BO", date: "27 settembre", dates: ["2026-09-27"], image: "image-mostra", description: "Laboratori creativi e visite per grandi e piccoli.", latitude: 44.4949, longitude: 11.3426, color: "#4e7966" },
  { title: "Teatro in Piazza", type: "Teatro", region: "Umbria", location: "Spoleto, PG", date: "28 settembre", dates: ["2026-09-28"], image: "image-mostra", description: "Spettacolo serale nel cuore del borgo.", latitude: 42.734, longitude: 12.738, color: "#d95d39" },
  { title: "Trekking delle Cascate", type: "Sport", region: "Marche", location: "Fiastra, MC", date: "29 settembre", dates: ["2026-09-29"], image: "image-castagna", description: "Escursione guidata tra boschi e acqua cristallina.", latitude: 43.035, longitude: 13.162, color: "#4e7966" },
  { title: "Sagra del Fungo Porcino", type: "Sagra", region: "Liguria", location: "Triora, IM", date: "30 settembre", dates: ["2026-09-30"], image: "image-castagna", description: "Cucina di montagna e prodotti del bosco.", latitude: 43.993, longitude: 7.763, color: "#d95d39" },
  { title: "Vendemmia in Cantina", type: "Famiglie", region: "Veneto", location: "Valdobbiadene, TV", date: "1 ottobre", dates: ["2026-10-01"], image: "image-mercatino", description: "Una giornata tra vigne, mosto e degustazioni.", latitude: 45.900, longitude: 12.101, color: "#e5b86e" },
  { title: "Mostra del Design Italiano", type: "Mostra", region: "Lombardia", location: "Milano, MI", date: "2 ottobre", dates: ["2026-10-02", "2026-10-03", "2026-10-04"], image: "image-mostra", description: "Oggetti, idee e progetti che hanno cambiato il quotidiano.", latitude: 45.4642, longitude: 9.19, color: "#4e7966" },
  { title: "Jazz tra i Borghi", type: "Concerto", region: "Abruzzo", location: "Santo Stefano di Sessanio, AQ", date: "2 ottobre", dates: ["2026-10-02"], image: "image-mercatino", description: "Jazz acustico e tramonto sulle montagne.", latitude: 42.343, longitude: 13.645, color: "#d95d39" },
  { title: "Festival del Cinema Breve", type: "Festival", region: "Sicilia", location: "Modica, RG", date: "3 ottobre", dates: ["2026-10-03", "2026-10-04"], image: "image-mostra", description: "Proiezioni, registi e storie da tutto il mondo.", latitude: 36.8588, longitude: 14.7608, color: "#4e7966" },
  { title: "Festa della Zucca", type: "Sagra", region: "Friuli-Venezia Giulia", location: "Venzone, UD", date: "4 ottobre", dates: ["2026-10-04"], image: "image-castagna", description: "Colori d'autunno, ricette locali e artigianato.", latitude: 46.333, longitude: 13.139, color: "#d95d39" },
  { title: "Mercato Vintage sul Naviglio", type: "Mercatino", region: "Lombardia", location: "Milano, MI", date: "5 ottobre", dates: ["2026-10-05"], image: "image-mercatino", description: "Abiti, vinili e oggetti con una seconda storia.", latitude: 45.448, longitude: 9.166, color: "#e5b86e" },
  { title: "Teatro per Tutti", type: "Teatro", region: "Puglia", location: "Lecce, LE", date: "6 ottobre", dates: ["2026-10-06"], image: "image-mostra", description: "Una commedia all'aperto per tutta la famiglia.", latitude: 40.3516, longitude: 18.175, color: "#d95d39" },
  { title: "Regata d'Autunno", type: "Sport", region: "Sardegna", location: "Alghero, SS", date: "10 ottobre", dates: ["2026-10-10"], image: "image-mercatino", description: "Vele, mare e una giornata sul lungomare.", latitude: 40.557, longitude: 8.319, color: "#4e7966" },
  { title: "Fiera del Cioccolato", type: "Fiera", region: "Umbria", location: "Perugia, PG", date: "11 ottobre", dates: ["2026-10-11"], image: "image-castagna", description: "Maestri cioccolatieri e dolci da tutta Italia.", latitude: 43.1107, longitude: 12.3908, color: "#e5b86e" },
  { title: "Concerto all'Alba", type: "Concerto", region: "Trentino-Alto Adige", location: "Riva del Garda, TN", date: "18 ottobre", dates: ["2026-10-18"], image: "image-mostra", description: "Musica dal vivo mentre il lago si risveglia.", latitude: 45.884, longitude: 10.841, color: "#d95d39" },
  { title: "Festa delle Castagne", type: "Sagra", region: "Campania", location: "Montella, AV", date: "25 ottobre", dates: ["2026-10-25"], image: "image-castagna", description: "Il grande appuntamento d'autunno dell'Irpinia.", latitude: 40.842, longitude: 15.018, color: "#d95d39" },
  { title: "Borgo delle Meraviglie", type: "Famiglie", region: "Lazio", location: "Calcata, VT", date: "31 ottobre", dates: ["2026-10-31"], image: "image-mostra", description: "Giochi, racconti e botteghe aperte nel borgo.", latitude: 42.22, longitude: 12.42, color: "#4e7966" },
  { title: "Fiera del Libro di Montagna", type: "Fiera", region: "Valle d'Aosta", location: "Aosta, AO", date: "31 ottobre", dates: ["2026-10-31"], image: "image-mostra", description: "Libri, autori e storie per leggere il paesaggio.", latitude: 45.737, longitude: 7.32, color: "#e5b86e" },
];

const dateOptions = [
  { value: "2026-09-26", day: "Sab", number: "26", month: "Set" },
  { value: "2026-09-27", day: "Dom", number: "27", month: "Set" },
  { value: "2026-09-28", day: "Lun", number: "28", month: "Set" },
  { value: "2026-09-29", day: "Mar", number: "29", month: "Set" },
  { value: "2026-09-30", day: "Mer", number: "30", month: "Set" },
  { value: "2026-10-01", day: "Gio", number: "1", month: "Ott" },
  { value: "2026-10-02", day: "Ven", number: "2", month: "Ott" },
  { value: "2026-10-03", day: "Sab", number: "3", month: "Ott" },
  { value: "2026-10-04", day: "Dom", number: "4", month: "Ott" },
  { value: "2026-10-05", day: "Lun", number: "5", month: "Ott" },
  { value: "2026-10-10", day: "Sab", number: "10", month: "Ott" },
  { value: "2026-10-11", day: "Dom", number: "11", month: "Ott" },
  { value: "2026-10-18", day: "Dom", number: "18", month: "Ott" },
  { value: "2026-10-25", day: "Dom", number: "25", month: "Ott" },
  { value: "2026-10-31", day: "Sab", number: "31", month: "Ott" },
];

const categoryOptions = ["Tutti", "Sagre", "Mercatini", "Mostre", "Concerti", "Festival", "Teatro", "Sport", "Famiglie", "Fiere"];
const categoryTypes: Record<string, string> = { Sagre: "Sagra", Mercatini: "Mercatino", Mostre: "Mostra", Concerti: "Concerto", Festival: "Festival", Teatro: "Teatro", Sport: "Sport", Famiglie: "Famiglie", Fiere: "Fiera" };

export default function EventDiscovery() {
  const [selectedDate, setSelectedDate] = useState("2026-09-26");
  const [selectedCategory, setSelectedCategory] = useState("Tutti");
  const [selectedEvent, setSelectedEvent] = useState<EventItem | null>(null);
  const [events, setEvents] = useState<EventItem[]>(demoEvents);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState("Aggiornamento automatico alle 01:00");
  const visibleEvents = events.filter((event) => event.dates.includes(selectedDate) && (selectedCategory === "Tutti" || event.type === categoryTypes[selectedCategory]));
  const availableDateOptions = Array.from(new Set(events.flatMap((event) => event.dates))).sort().map((value) => {
    const date = new Date(`${value}T12:00:00`);
    return { value, day: date.toLocaleDateString("it-IT", { weekday: "short" }).replace(".", ""), number: date.getDate().toString(), month: date.toLocaleDateString("it-IT", { month: "short" }).replace(".", "") };
  });

  useEffect(() => {
    const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
    fetch(`${apiBase}/api/events?limit=100`)
      .then((response) => response.ok ? response.json() : Promise.reject(new Error("API non disponibile")))
      .then((data: { items?: Array<{ title: string; short_description?: string; description?: string; starts_at?: string; ends_at?: string; official_url?: string; source_url?: string; latitude?: number; longitude?: number; category_name?: string; municipality?: string; province?: string; region?: string }> }) => {
        const apiEvents = (data.items ?? []).filter((item) => item.starts_at && item.latitude != null && item.longitude != null).map((item) => {
          const start = new Date(item.starts_at as string);
          const end = item.ends_at ? new Date(item.ends_at) : start;
          const dates: string[] = [];
          for (const cursor = new Date(start); cursor <= end; cursor.setUTCDate(cursor.getUTCDate() + 1)) dates.push(cursor.toISOString().slice(0, 10));
          return {
            title: item.title,
            type: item.category_name ?? "Evento",
            region: item.region ?? "Lazio",
            location: [item.municipality, item.province].filter(Boolean).join(", "),
            date: start.toLocaleDateString("it-IT", { day: "numeric", month: "long" }),
            dates,
            image: "image-mostra",
            description: item.short_description ?? item.description ?? "Evento del Comune di Viterbo.",
            latitude: item.latitude as number,
            longitude: item.longitude as number,
            color: "#d95d39",
            sourceUrl: item.source_url,
            officialUrl: item.official_url,
          };
        });
        if (apiEvents.length > 0) {
          setEvents(apiEvents);
          setSelectedDate(apiEvents[0].dates[0]);
        }
      })
      .catch(() => setEvents(demoEvents));
  }, []);

  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => event.key === "Escape" && setSelectedEvent(null);
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, []);

  const openEvent = (event: EventItem) => setSelectedEvent(event);

  const refreshDatabase = async () => {
    setIsRefreshing(true);
    setRefreshMessage("Aggiornamento in corso...");

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL;
      if (!apiBase) {
        throw new Error("API online non configurata. Imposta NEXT_PUBLIC_API_URL su Vercel.");
      }
      const response = await fetch(`${apiBase}/api/admin/refresh-db`, { method: "POST" });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.message ?? "Aggiornamento non riuscito");
      }
      setRefreshMessage(`Database aggiornato: ${data.updated_events ?? 0} eventi`);
    } catch (error) {
      setRefreshMessage(error instanceof Error ? error.message : "Aggiornamento non riuscito");
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <section className="discover" id="scopri">
      <div className="section-heading"><div><p className="eyebrow">Scegli quando uscire</p><h2>Che giorno<br /><em>hai libero?</em></h2></div><div className="result-count"><strong>{visibleEvents.length}</strong> eventi trovati</div></div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "12px", marginBottom: "12px", flexWrap: "wrap" }}>
        <div className="selected-date-note" style={{ margin: 0 }}>{refreshMessage}</div>
        <button type="button" onClick={refreshDatabase} disabled={isRefreshing} style={{ border: "none", borderRadius: "999px", background: "#d95d39", color: "white", padding: "0.7rem 1rem", cursor: isRefreshing ? "wait" : "pointer", fontWeight: 700 }}>
          {isRefreshing ? "Aggiornamento..." : "Aggiorna DB adesso"}
        </button>
      </div>
      <div className="date-picker" aria-label="Seleziona la data degli eventi">
        <div className="date-picker-label">Eventi disponibili <span>{availableDateOptions.length > 0 ? new Date(`${availableDateOptions[0].value}T12:00:00`).getFullYear() : ""}</span></div>
        <div className="date-options">{availableDateOptions.map((date) => <button className={date.value === selectedDate ? "date-option active" : "date-option"} key={date.value} onClick={() => setSelectedDate(date.value)} type="button" aria-pressed={date.value === selectedDate}><small>{date.day}</small><strong>{date.number}</strong><small>{date.month}</small></button>)}</div>
        <button className="calendar-button" type="button" aria-label="Apri il calendario">▦</button>
      </div>
      <div className="category-filter" aria-label="Filtra per categoria"><span className="filter-label">Tipo di evento</span>{categoryOptions.map((category) => <button className={category === selectedCategory ? "category-chip active" : "category-chip"} key={category} onClick={() => setSelectedCategory(category)} type="button" aria-pressed={category === selectedCategory}>{category}</button>)}<a className="map-filter-link" href="#mappa">Mappa <span>↘</span></a></div>
      <div className="selected-date-note">Eventi per <strong>{new Date(`${selectedDate}T12:00:00`).toLocaleDateString("it-IT", { weekday: "long", day: "numeric", month: "long" })}</strong><span> · Tutta Italia</span></div>
      {visibleEvents.length > 0 ? <div className="event-grid">{visibleEvents.map((event) => <article className="event-card" key={event.title}><div className={`event-image ${event.image}`}><span>{event.date.toUpperCase()}</span></div><div className="event-content"><p className="event-type">{event.type} · {event.region}</p><h3>{event.title}</h3><p>{event.location}</p><p className="event-description">{event.description}</p><button className="event-detail-button" type="button" onClick={() => openEvent(event)}>Scopri l&apos;evento <span>↗</span></button></div></article>)}</div> : <div className="empty-results"><strong>Nessun evento trovato.</strong><span>Prova a cambiare data o categoria.</span></div>}
      <div className="map-section" id="mappa"><div className="map-heading"><div><p className="eyebrow">Esplora sulla mappa</p><h2>Succede<br /><em>qui vicino.</em></h2></div><div className="map-intro"><p>Gli eventi mostrati corrispondono alla data che hai scelto.</p><a href="#mappa">Usa la mia posizione <span>↗</span></a></div></div><MapIsland events={visibleEvents} selectedDate={selectedDate} onEventClick={(mapEvent) => { const event = visibleEvents.find((item) => item.title === mapEvent.title); if (event) openEvent(event); }} /></div>
      {selectedEvent && <div className="event-modal-backdrop" role="presentation" onMouseDown={() => setSelectedEvent(null)}><article className="event-modal" role="dialog" aria-modal="true" aria-labelledby="event-modal-title" onMouseDown={(event) => event.stopPropagation()}><button className="modal-close" type="button" onClick={() => setSelectedEvent(null)} aria-label="Chiudi dettaglio evento">×</button><div className={`modal-image ${selectedEvent.image}`}><span>{selectedEvent.date.toUpperCase()}</span></div><div className="modal-content"><p className="event-type">{selectedEvent.type} · {selectedEvent.region}</p><h2 id="event-modal-title">{selectedEvent.title}</h2><p className="modal-location">{selectedEvent.location}</p><p>{selectedEvent.description} Una giornata per scoprire il territorio, incontrare le persone del luogo e vivere l&apos;evento con calma.</p><div className="modal-facts"><span><strong>Quando</strong>{selectedEvent.date}</span><span><strong>Dove</strong>{selectedEvent.location.split(" · ")[0]}</span></div><a className="modal-source" href={getEventSourceUrl(selectedEvent)} target="_blank" rel="noreferrer">{selectedEvent.officialUrl || selectedEvent.sourceUrl ? "Vai alla fonte ufficiale" : "Cerca la fonte dell'evento"} <span>↗</span></a></div></article></div>}
    </section>
  );
}
