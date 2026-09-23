"use client";

import { useEffect } from "react";
import { Circle, CircleMarker, MapContainer, TileLayer, ZoomControl, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import type { PlaceItem } from "./event-discovery";

export type MapEvent = {
  title: string;
  location: string;
  date: string;
  latitude: number;
  longitude: number;
  color: string;
};

type EventMapProps = { events: MapEvent[]; selectedDate: string; onEventClick: (event: MapEvent) => void };

type ExtendedEventMapProps = EventMapProps & { departure: PlaceItem | null; radiusKm: number | "all" };

function MapViewport({ departure, radiusKm, events }: { departure: PlaceItem | null; radiusKm: number | "all"; events: MapEvent[] }) {
  const map = useMap();
  useEffect(() => {
    if (departure && typeof radiusKm === "number") {
      const center = L.latLng(departure.latitude, departure.longitude);
      map.fitBounds(center.toBounds(radiusKm * 2000), { padding: [28, 28] });
      return;
    }
    if (departure) {
      map.setView([departure.latitude, departure.longitude], 8);
      return;
    }
    if (events.length > 0) {
      map.fitBounds(L.latLngBounds(events.map((event) => [event.latitude, event.longitude])), { padding: [28, 28] });
    }
  }, [departure, radiusKm, events, map]);
  return null;
}

export default function EventMap({ events, selectedDate, onEventClick, departure, radiusKm }: ExtendedEventMapProps) {
  return (
    <div className="map-frame">
      <MapContainer center={[42.55, 12.4]} zoom={6} scrollWheelZoom={false} zoomControl={false} className="event-map">
        <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <ZoomControl position="bottomright" />
        <MapViewport departure={departure} radiusKm={radiusKm} events={events} />
        {departure && typeof radiusKm === "number" && <Circle center={[departure.latitude, departure.longitude]} radius={radiusKm * 1000} pathOptions={{ color: "#d95d39", fillColor: "#d95d39", fillOpacity: 0.08, weight: 2 }} />}
        {departure && <CircleMarker center={[departure.latitude, departure.longitude]} radius={13} pathOptions={{ color: "#1e2d2b", weight: 3, fillColor: "#e5b86e", fillOpacity: 1 }} />}
        {events.map((event) => (
          <CircleMarker key={event.title} center={[event.latitude, event.longitude]} radius={10} pathOptions={{ color: "#f5f1e8", weight: 3, fillColor: event.color, fillOpacity: 1 }} eventHandlers={{ click: () => onEventClick(event) }} />
        ))}
      </MapContainer>
      <div className="map-caption"><span className="map-pulse" /> <strong>{events.length} eventi</strong> il {new Date(`${selectedDate}T12:00:00`).toLocaleDateString("it-IT", { day: "numeric", month: "long" })} <span className="map-caption-arrow">↗</span></div>
    </div>
  );
}
