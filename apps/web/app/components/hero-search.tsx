"use client";

import { FormEvent, useState } from "react";

export default function HeroSearch() {
  const [query, setQuery] = useState("");

  const submit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = query.trim();
    const params = new URLSearchParams(window.location.search);
    if (trimmed) {
      params.set("partenza", trimmed);
      params.set("radius", params.get("radius") ?? "100");
    }
    const target = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ""}#scopri`;
    window.history.replaceState(null, "", target);
    window.dispatchEvent(new CustomEvent("feste-hero-search", { detail: { query: trimmed } }));
    document.getElementById("scopri")?.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <form className="search" onSubmit={submit}>
      <input aria-label="Cerca località di partenza" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Cerca una città di partenza..." />
      <button type="submit">Cerca <span>↗</span></button>
    </form>
  );
}
