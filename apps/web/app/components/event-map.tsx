"use client";

import { CircleMarker, MapContainer, TileLayer, ZoomControl } from "react-leaflet";
import "leaflet/dist/leaflet.css";

export type MapEvent = {
  title: string;
  location: string;
  date: string;
  latitude: number;
  longitude: number;
  color: string;
};

type EventMapProps = { events: MapEvent[]; selectedDate: string; onEventClick: (event: MapEvent) => void };

export default function EventMap({ events, selectedDate, onEventClick }: EventMapProps) {
  return (
    <div className="map-frame">
      <MapContainer center={[42.55, 12.4]} zoom={6} scrollWheelZoom={false} zoomControl={false} className="event-map">
        <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
        <ZoomControl position="bottomright" />
        {events.map((event) => (
          <CircleMarker key={event.title} center={[event.latitude, event.longitude]} radius={10} pathOptions={{ color: "#f5f1e8", weight: 3, fillColor: event.color, fillOpacity: 1 }} eventHandlers={{ click: () => onEventClick(event) }} />
        ))}
      </MapContainer>
      <div className="map-caption"><span className="map-pulse" /> <strong>{events.length} eventi</strong> il {new Date(`${selectedDate}T12:00:00`).toLocaleDateString("it-IT", { day: "numeric", month: "long" })} <span className="map-caption-arrow">↗</span></div>
    </div>
  );
}
