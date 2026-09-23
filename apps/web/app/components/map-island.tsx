"use client";

import dynamic from "next/dynamic";
import type { MapEvent } from "./event-map";
import type { PlaceItem } from "./event-discovery";

const EventMap = dynamic(() => import("./event-map"), { ssr: false });

type MapIslandProps = { events: MapEvent[]; selectedDate: string; onEventClick: (event: MapEvent) => void; departure: PlaceItem | null; radiusKm: number | "all" };

export default function MapIsland({ events, selectedDate, onEventClick, departure, radiusKm }: MapIslandProps) {
  return <EventMap events={events} selectedDate={selectedDate} onEventClick={onEventClick} departure={departure} radiusKm={radiusKm} />;
}
