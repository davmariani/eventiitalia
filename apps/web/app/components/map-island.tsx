"use client";

import dynamic from "next/dynamic";
import type { MapEvent } from "./event-map";

const EventMap = dynamic(() => import("./event-map"), { ssr: false });

type MapIslandProps = { events: MapEvent[]; selectedDate: string; onEventClick: (event: MapEvent) => void };

export default function MapIsland({ events, selectedDate, onEventClick }: MapIslandProps) {
  return <EventMap events={events} selectedDate={selectedDate} onEventClick={onEventClick} />;
}
