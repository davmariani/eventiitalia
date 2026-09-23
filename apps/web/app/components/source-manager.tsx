"use client";

import { FormEvent, useEffect, useState } from "react";

type EventSource = {
  id: number;
  name: string;
  url: string;
  municipality?: string | null;
  province?: string | null;
  region: string;
  enabled: boolean;
};

const apiBase = () => process.env.NEXT_PUBLIC_API_URL;

export default function SourceManager() {
  const [sources, setSources] = useState<EventSource[]>([]);
  const [message, setMessage] = useState("Aggiungi pagine elenco o pagine dettaglio evento.");
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    const base = apiBase();
    if (!base) {
      setMessage("API online non configurata.");
      return;
    }
    fetch(`${base}/api/admin/sources`)
      .then((response) => response.ok ? response.json() : Promise.reject(new Error("Fonti non disponibili")))
      .then((data: EventSource[]) => setSources(data))
      .catch(() => setMessage("Non riesco a leggere le fonti salvate."));
  }, []);

  const addSource = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const base = apiBase();
    if (!base) {
      setMessage("API online non configurata.");
      return;
    }

    const form = new FormData(event.currentTarget);
    const payload = {
      name: String(form.get("name") ?? "").trim(),
      url: String(form.get("url") ?? "").trim(),
      region: String(form.get("region") ?? "Italia").trim() || "Italia",
      province: String(form.get("province") ?? "").trim() || null,
      municipality: String(form.get("municipality") ?? "").trim() || null,
      latitude: Number(form.get("latitude")) || null,
      longitude: Number(form.get("longitude")) || null,
    };

    setIsSaving(true);
    setMessage("Salvataggio fonte...");
    try {
      const response = await fetch(`${base}/api/admin/sources`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail ?? "Fonte non salvata");
      }
      setSources((current) => [data, ...current]);
      event.currentTarget.reset();
      setMessage("Fonte salvata. Ora puoi aggiornare il DB.");
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Fonte non salvata");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <section className="source-manager" id="segnala">
      <div className="source-heading">
        <div>
          <p className="eyebrow">Fonti eventi</p>
          <h2>Aggiungi pagine<br /><em>da monitorare.</em></h2>
        </div>
        <p>Incolla una pagina con elenco eventi, poi usa “Aggiorna DB adesso”.</p>
      </div>
      <form className="source-form" onSubmit={addSource}>
        <label>Nome fonte<input name="name" placeholder="Umbriatourism" required /></label>
        <label>URL pagina eventi<input name="url" placeholder="https://www.umbriatourism.it/it/eventi" required type="url" /></label>
        <label>Regione<input name="region" placeholder="Umbria" defaultValue="Italia" /></label>
        <label>Provincia<input name="province" placeholder="PG" /></label>
        <label>Comune<input name="municipality" placeholder="Perugia" /></label>
        <label>Latitudine<input name="latitude" placeholder="43.1107" inputMode="decimal" /></label>
        <label>Longitudine<input name="longitude" placeholder="12.3908" inputMode="decimal" /></label>
        <button type="submit" disabled={isSaving}>{isSaving ? "Salvataggio..." : "Salva fonte"}</button>
      </form>
      <div className="source-message">{message}</div>
      {sources.length > 0 && (
        <div className="source-list">
          {sources.map((source) => (
            <a href={source.url} key={source.id} target="_blank" rel="noreferrer">
              <strong>{source.name}</strong>
              <span>{source.region}{source.province ? ` · ${source.province}` : ""}</span>
            </a>
          ))}
        </div>
      )}
    </section>
  );
}
