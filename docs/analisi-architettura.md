# Analisi architetturale e piano di sviluppo iniziale

Questo documento raccoglie l’analisi preliminare del progetto, in linea con le richieste del brief e con l’obiettivo di costruire una piattaforma italiana affidabile per rispondere alla domanda: “Ho questa giornata libera: dove posso andare e cosa posso fare?”

> Stato: solo analisi architetturale e documentazione. Non è stato ancora creato il codice applicativo né i file di progetto. L’implementazione vera e propria dovrà partire solo dopo approvazione dell’architettura.

---

## 1. Architettura definitiva proposta

### Obiettivo strategico
Il sistema deve essere un portale di eventi italiani orientato alla scoperta locale e alla pianificazione della giornata, non solo una mappa con marker. La parte di valore è la combinazione di:

- ricerca per luogo, data, distanza e interessi;
- mappa interattiva con eventi rilevanti;
- dati strutturati e affidabili;
- deduplicazione tra fonti multiple;
- geocodifica efficiente e cache;
- filtri geografici e per categoria;
- pagine di dettaglio SEO-friendly;
- pipeline di ingestione automatica controllata da admin.

### Architettura logica consigliata

1. Frontend: Next.js + App Router + TypeScript + Tailwind CSS
2. Mappa: MapLibre GL JS (preferita) per controllo, costo e compatibilità con standard aperti; Leaflet è backup valido in caso di esigenze MVP più semplici.
3. API backend: FastAPI + Pydantic + SQLAlchemy + PostgreSQL/PostGIS + Alembic
4. Ingestion: servizio dedicato in Python, separato dal core API, con connettori per sorgenti esterne
5. Coda job / scheduling: Redis opzionale per job schedulati e cache, ma non necessario all’inizio per l’MVP
6. Storage: PostgreSQL + PostGIS come fonte di verità per dati eventi, geografie e località
7. File statici e asset: CDN o storage statico per immagini e file generati
8. Admin: area dedicata separata, con autenticazione, controllo di validazione e pubblicazione

### Principi di progettazione
- Separare nettamente core, ingestion, deduplication e geocoding
- Nessun parser sorgente nel core applicativo
- Nessun blocco monolitico su una sola fonte
- Usare eventi e pipeline idempotenti
- Separare raw data da normalized event
- Certificare ogni fonte prima di integrarla

### Scelta presunta per l’MVP

- MapLibre GL JS è preferibile a Leaflet perché è più moderna, orientata a visualizzazioni complesse, supporta cluster, controlli moderni e lascia più spazio a evoluzioni future (heatmap, layer avanzati, visualizzazione tematizzate).
- Leaflet resta una scelta compatibile se l’obiettivo è minimizzare il peso iniziale dell’MVP.
- In ogni caso, il frontend deve essere progettato con un layer di astrazione mappa, così da poter cambiare provider in futuro senza toccare l’applicazione.

---

## 2. Struttura completa delle cartelle

```text
/
├── apps/
│   ├── web/                     # Next.js frontend
│   │   ├── app/
│   │   ├── components/
│   │   ├── lib/
│   │   ├── styles/
│   │   └── public/
│   └── api/                    # FastAPI backend
│       ├── alembic/
│       ├── app/
│       ├── migrations/
│       └── tests/
├── services/
│   ├── ingestion/
│   │   ├── connectors/
│   │   ├── jobs/
│   │   ├── parsers/
│   │   ├── scheduler/
│   │   └── validators/
│   ├── crawler/
│   │   ├── tasks/
│   │   └── runners/
│   ├── geocoding/
│   │   ├── providers/
│   │   ├── cache/
│   │   └── strategies/
│   ├── ai/
│   │   ├── extractors/
│   │   ├── prompts/
│   │   └── validation/
│   └── shared/
│       ├── models/
│       ├── schemas/
│       ├── utils/
│       └── constants/
├── packages/
│   ├── shared/
│   │   ├── types/
│   │   ├── enums/
│   │   └── validators/
│   ├── config/
│   │   ├── env/
│   │   └── rules/
│   └── ui/
│       ├── components/
│       └── design-system/
├── infrastructure/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── docker-compose.dev.yml
│   │   ├── docker-compose.staging.yml
│   │   └── docker-compose.prod.yml
│   ├── nginx/
│   ├── postgres/
│   ├── redis/
│   └── monitoring/
├── docs/
│   ├── architecture.md
│   ├── database.md
│   ├── api.md
│   ├── sources.md
│   ├── ingestion.md
│   ├── geocoding.md
│   ├── deployment.md
│   ├── security.md
│   ├── admin.md
│   └── roadmap.md
├── scripts/
│   ├── bootstrap/
│   ├── maintenance/
│   └── import/
├── tests/
│   ├── api/
│   ├── integration/
│   ├── parsers/
│   ├── deduplication/
│   └── e2e/
├── .env.example
├── .gitignore
├── README.md
├── docker-compose.yml
├── Makefile
└── package.json
```

---

## 3. Schema dei componenti

### 3.1 Frontend
- SearchForm: luogo, data, distanza, interessi
- EventListPanel: lista eventi con card e paginazione
- MapPanel: layer mappa, marker, popup, cluster
- FilterDrawer: filtri e filtri avanzati
- EventDetailPage: pagina evento con SEO metadata
- LocationPage: pagine per regioni/comuni/borghi
- AdminPanel: dashboard di import e di validazione

### 3.2 Backend API
- EventQueryService: filtri, ricerca geospaziale, ranking
- EventDetailService: dettaglio e EventSchema.org
- SourceManagementService: gestione fonti e monitoraggio
- ImportOrchestrator: orchestrazione importazione
- DeduplicationService: matches e probabilità duplicato
- GeocodingService: cache, provider routing, validazioni
- PublishingService: passa da raw → normalized → Event published

### 3.3 Ingestion
- SourceConnector interface
- Discoverer
- Fetcher
- Parser
- Normalizer
- Validator
- ImportJob
- RawRecordStore

### 3.4 Database layer
- SQLAlchemy models per eventi, locali, fonti, import jobs, revisioni, geocoding cache
- PostGIS support per bbox, distance query, punti e ricerche geografiche

---

## 4. Schema database

### Entità chiave

#### Event
- id
- slug
- title
- short_description
- description
- category_id
- venue_id
- organizer_id
- start_datetime
- end_datetime
- timezone
- all_day
- recurrence_rule
- price_min
- price_max
- is_free
- booking_required
- booking_url
- official_url
- image_url
- latitude
- longitude
- address
- postal_code
- municipality
- province
- region
- country
- source_id
- source_external_id
- source_url
- source_last_checked_at
- source_published_at
- status
- confidence_score
- verification_status
- created_at
- updated_at
- published_at

#### Source
- id
- name
- base_url
- type
- geographic_scope
- update_frequency
- last_success
- last_error
- terms_checked
- robots_checked
- license
- attribution_required
- enabled
- priority
- reliability_score
- parser_name
- notes

#### Venue
- id
- name
- address
- municipality
- province
- region
- latitude
- longitude
- is_virtual

#### Location
- id
- type (region/province/comune/borough)
- name
- parent_id
- codice_istat
- latitude
- longitude
- geometry (PostGIS)

#### Category
- id
- name
- slug
- parent_id
- icon_key
- color_code

#### Organizer
- id
- name
- type
- website
- contact_email
- phone

#### EventDate / EventOccurrence
Per gestire evento in una sola giornata, più giorni, weekend, ricorrenze, festival.
- id
- event_id
- start_datetime
- end_datetime
- recurrence_type
- occurrence_label
- is_all_day

Questa tabella è fondamentale per separare la struttura dell’evento dalla sua programmazione temporale.

#### EventSource
Rappresenta il collegamento tra evento e fonte.
- id
- event_id
- source_id
- external_id
- url
- last_seen_at
- is_primary

#### ImportJob
- id
- source_id
- started_at
- finished_at
- status
- records_found
- records_created
- records_updated
- duplicates
- errors
- job_hash

#### CrawlResult / RawData
- id
- source_id
- job_id
- raw_payload
- format
- content_hash
- fetched_at

#### GeocodingCache
- id
- normalized_query
- provider_name
- latitude
- longitude
- confidence
- created_at

#### EventDuplicate
- id
- canonical_event_id
- duplicate_event_id
- duplicate_type (exact / probable)
- score
- created_at

#### EventRevision
- id
- event_id
- changed_by
- change_summary
- previous_payload
- new_payload
- created_at

#### AdminUser
- id
- email
- password_hash
- role
- created_at

#### EventReport
- id
- event_id
- reported_by
- report_type
- notes
- status
- created_at

### Stati evento consigliati
- DRAFT
- AUTOMATIC
- TO_REVIEW
- VERIFIED
- PUBLISHED
- CANCELLED
- EXPIRED
- REJECTED

### Considerazione importante
Non si può assumere che ogni evento abbia un solo campo start/end. La struttura deve supportare:
- evento singolo;
- evento di più giorni consecutivi;
- weekend ricorrenti;
- eventi ogni domenica;
- date specifiche;
- aperture straordinarie in notti selezionate;
- festival con molte date;
- musei con aperture eccezionali.

Per questo la tabella Event + EventOccurrence è la scelta più robusta e futura.

---

## 5. Diagramma del flusso

```text
FONTI
  ↓
ACQUISIZIONE
  ↓
RAW DATA
  ↓
PARSING
  ↓
NORMALIZZAZIONE
  ↓
DEDUPLICAZIONE
  ↓
GEOCODIFICA
  ↓
VALIDAZIONE
  ↓
DATABASE
  ↓
PUBBLICAZIONE
  ↓
API
  ↓
MAPPA / SITO
```

### Flusso dettagliato
1. Una fonte è attivata
2. Il collector fetcha dati in base a tipo e frequenza
3. Il payload grezzo viene salvato in raw storage con hash
4. Parser e normalizer trasformano in modello standard
5. Sistema di deduplicazione confronta titolo, data, venue, URL, external ID, posizione
6. Geocoder controlla cache e produce coordinate
7. Validatore applica regole di affidabilità, date, campi obbligatori e status
8. Eventi validi vanno in database
9. Filter / ranking / search li rendono disponibili a API e frontend
10. Mappa, lista e pagina evento mostrano i risultati

---

## 6. Elenco delle prime fonti consigliate da integrare

### A. Fonti nazionali
1. Ministero della Cultura
   - Tipo: API/open data/HTML variabile
   - Vantaggio: autorità centrale, molto importante per musei, siti culturali, iniziative storiche
   - Limiti: struttura non sempre uniforme; alcuni contenuti sparsi tra portali distinti
   - Verifica: licenza, robots, eventuali API pubbliche, date di aggiornamento

2. Sistema dei musei e luoghi della cultura
   - Tipo: open data, API o HTML di portali dedicati
   - Vantaggio: disciplina culturale utile per musei, aperture straordinarie, mostre
   - Limiti: non sempre centralizzato

3. Turismo Italia / IAT / portali turistici nazionali
   - Tipo: feed JSON/RSS o HTML
   - Vantaggio: eventi a livello nazionale, eventi turistici, grandi manifestazioni
   - Limiti: variabilità di schema e qualità dei dati

4. Ticketmaster Discovery API / Discovery Feed
   - Tipo: API ufficiale
   - Vantaggio: dati strutturati, evento musicale, festival, spettacoli, grandi eventi
   - Limiti: non copre tutta Italia; spesso più concentrato su grandi città e eventi commerciali

5. Eventbrite (dove consentito e conforme alle policy)
   - Tipo: API / feed / HTML
   - Vantaggio: traffico reale, eventi vari
   - Limiti: non universalmente disponibile per tutte le località

6. Datasets OpenData italiani / ISTAT / dati geografici
   - Tipo: open data
   - Vantaggio: dati territoriali ufficiali utili per località, province, comuni e codici ISTAT

### B. Regioni (priorità per copertura nazionale)
Vanno aggiunte come campionamento prioritario, regione per regione, iniziando dalle più attive e con calendario eventi pubblici:

1. Lazio
2. Toscana
3. Emilia-Romagna
4. Veneto
5. Lombardia
6. Campania
7. Puglia
8. Sicilia
9. Sardegna
10. Marche
11. Piemonte
12. Abruzzo
13. Umbria
14. Molise
15. Calabria
16. Basilicata
17. Friuli Venezia Giulia
18. Trentino-Alto Adige
19. Valle d’Aosta
20. Liguria

Per ogni regione verificarne:
- portale turistico ufficiale;
- calendario eventi;
- API o feed JSON;
- RSS;
- sitemap;
- JSON incorporato;
- open data;
- dataset geografici e amministrativi.

### C. Province / città metropolitane
- Calendari eventi dei Comuni capoluogo
- Eventi di provincia e macro-aree
- Rassegne culturali e manifestazioni turistiche

### D. Comuni
Priorità da integrare come prime fonti operative:
- Roma
- Viterbo
- Firenze
- Napoli
- Bologna
- Milano
- Torino
- Palermo
- Cagliari
- Verona
- Trento
- Perugia
- etc.

### E. Pro Loco
- Tra le sorgenti più importanti per sagre, feste patronali, mercatini, tradizioni
- Spesso pubblicano eventi con grande qualità locale ma schema non standardizzato

### F. Musei
- Musei statali e civici
- Musei archeologici
- Collezioni private e musei del territorio

### G. Parchi
- Parchi nazionali
- Parchi regionali
- Natura, trekking, iniziative ambientali

### H. Teatri
- Teatri di città e province
- Compagnie, teatri stabili, festival teatrali

### I. Festival
- Festival musicali, cinematografici, letterari, enogastronomici, folk

### L. Enti turistici
- IAT, uffici turismo dei comuni, enti di promozione del territorio

### M. Associazioni locali
- Associazioni culturali, storiche, folkloristiche, sportive

### N. Piattaforme di ticketing
- Eventbrite, Ticketmaster, TryBooking (se disponibili)

### O. Altre fonti autorevoli
- Università e centri culturali
- biblioteche
- fondazioni
- sedi storiche
- parchi e riserve
- reti di eventi delle amministrazioni

---

## 7. Per ciascuna fonte: tipo, verifiche e limiti

### Tipologia sorgente da preferire
1. API ufficiale
2. Open data
3. RSS
4. Feed JSON/XML/ICS
5. Sitemap
6. HTML pubblico e consentito

### Verifiche obbligatorie prima di usare una sorgente
- condizioni d’uso;
- robots.txt;
- licenza e copyright;
- rate limits;
- mandatory user-agent;
- anti-bot e CAPTCHA;
- autenticazione richiesta;
- schema dati e affidabilità.

### Esempi di limiti da monitorare
- Data pubblicata in formato non standard
- Risorse chiuse o non raggiungibili
- Campi obbligatori assenti
- Eventi duplicati su più pagine
- Link di prenotazione non permanenti
- Nessun field per coordinate o comune
- Feed con aggiornamenti inconsistenti

### Regola di integrità
Nessuna fonte deve essere usata se non è stata verificata legalmente e tecnicamente. Non si deve aggirare CAPTCHA, non si devono simulare utenti, non si devono bypassare protezioni anti-bot.

---

## 8. Struttura delle API

### API REST progettate per l’MVP
- GET /api/events
- GET /api/events/{id}
- GET /api/events/map
- GET /api/events/nearby
- GET /api/events/weekend
- GET /api/categories
- GET /api/regions
- GET /api/provinces
- GET /api/municipalities
- GET /api/locations/search
- POST /api/reports
- POST /api/admin/events
- GET /api/admin/dashboard
- GET /api/admin/sources
- POST /api/admin/sources/{id}/run
- POST /api/admin/sources/{id}/disable

### Query importanti
- data
- start_date/end_date
- luogo
- distanza_massima
- bbox (north/south/east/west)
- categoria
- sottocategoria
- gratuito
- payment_required
- children_friendly
- accessible
- indoor/outdoor
- part_of_day
- recurrence

### Protocolli
- OpenAPI generato da FastAPI
- JSON standardizzato
- Filtri server-side, non JavaScript-side
- Nessuna API ad hoc senza documentazione

---

## 9. Strategia di caching

### Obiettivo
Ridurre carico su database e provider, senza invalidare dati cruciali.

### Categorie cache
1. Homepage
   - risultati popolari, weekend e filtri standard
2. Eventi weekend
   - calcoli frequenti su regioni e partenza
3. Dati geografici
   - regioni, province, comuni, CAP
4. Query comuni
   - autocompletamento e lookup area
5. Geocoding
   - chiave: indirizzo + comune + provincia + CAP + paese
6. Risultati mappa
   - bounding box per data e categorie

### Invalida correttamente
- modifica evento
- update di fonte
- geocode ricalcolato
- cancellazione logica o pubblicazione

### Strategie consigliate
- Redis per cache volatile e job queue
- TTL moderato per query geocodifica e località
- cache disabilitata per dati amministrativi critici in aggiornamento continuo

---

## 10. Strategia di deduplicazione

### Obiettivo
Un evento condiviso da più fonti non deve apparire 5 volte.

### Principio
Ogni evento deve avere un’identità unica logica, ma può avere molte `EventSource` e molte `source_external_id`.

### Regole di confronto
- titolo normalizzato
- similarità titolo
- data e orario
- comune e provincia
- coordinate
- venue
- organizzatore
- URL
- external ID

### Livelli di risultato
- exact match: stesso evento
- probable duplicate: elevata probabilità, da validare

### Regola documentata di prevalenza
Quando due fonti riportano dati diversi, la fonte più autorevole prevale. Esempio:
- Comune > Pro Loco > portale turistico locale > social/terziario

### Struttura consigliata
- `Event` come entità canonica
- `EventSource` per collegare una fonte a un evento
- `EventDuplicate` per registrare casi sospetti e revisioni manuali

---

## 11. Strategia di geocodifica

### Interfaccia consigliata
```python
class GeocodingProvider(Protocol):
    def geocode(self, address: str, municipality: str | None = None, province: str | None = None, postal_code: str | None = None, country: str = "IT") -> GeocodedPoint | None:
        ...
```

### Provider intercambiabili
- provider pubblico (solo in dev / valutazione)
- provider commerciale (produzione)
- eventuale istanza interna
- dataset geografici ISTAT/ANPR/territoriali ufficiali

### Cache obbligatoria
- chiave normalizzata: `indirizzo + comune + provincia + CAP + paese`
- evitare richieste ripetute per i medesimi indirizzi

### Regola di sicurezza
Nominatim pubblico non va usato per geocodifica massiva in produzione. È compatibile per test e bootstrap ma non per carichi reali senza policy e rate-limit rispettati.

### Priorità
1. Dati geocodificati direttamente dalla fonte
2. Cache locale
3. Provider ufficiale o commerciale stabilizzato
4. Fallback con approccio locale e controllato

---

## 12. Strategia SEO

### Obiettivo
Il sito deve essere trovabile e comprensibile per utenti e crawler.

### Requisiti SEO
- SSR / static generation dove appropriato
- metadata dinamici
- canonical URL
- sitemap.xml
- sitemap eventi
- sitemap località
- robots.txt
- OpenGraph
- Twitter Cards
- JSON-LD
- Schema.org Event per eventi
- schema geografici per luoghi

### URL
- /eventi/sagra-della-castagna-vallerano-2026
- /lazio/roma
- /lazio/viterbo
- /borghi/calcata

### Eventi scaduti
Non vanno eliminati, ma marcati come terminati e mantenuti con contenuto storico, utile anche per SEO.

---

## 13. Strategia di deployment

### Ambiente consigliato
- Development: Docker Compose con servizi leggeri
- Staging: ambiente isolato con dati test e validazione funzionale
- Production: cluster orchestrato o ambiente containerizzato basato su servizi dedicati

### Componenti
- app web Next.js
- API FastAPI
- PostgreSQL + PostGIS
- Redis (opzionale ma consigliato)
- job scheduler / queue worker
- reverse proxy / ingress
- monitoring

### Configurazione
- `.env` per ambiente locale
- `.env.example` come template
- secret non in repository
- variabili per DB, geocoder, mail, admin auth

### Deployment raccomandato iniziale
- Docker Compose per sviluppo
- Cloud o VM per staging e produzione
- CDN per asset statici e immagini
- backup regolari DB
- monitoraggio errori e health checks

---

## 14. Costi potenziali dei servizi esterni

### Costi principali da considerare
- database managed PostgreSQL/PostGIS
- provider geocoding commerciale
- provider map tiles / map service (se non usato open-source)
- hosting web/backend
- storage immagini
- provider di monitoring e log
- eventuale AI extraction (solo opzionale)
- email / notifiche / admin dashboard

### Valore di costo-stima
- MVP: basso/moderato se si usa open source + servizi essenziali
- Fase 2 e 3: incrementi legati a API esterne, geocoding, immagini e traffico
- Evitare dipendenze troppo forti da un singolo provider

### Strategia di controllo costi
- usare open source per frontend e backend
- trattare geocoding e map provider come componenti sostituibili
- evitare AI costosa come componente base; usarla solo su casi dove aggiunge valore reale

---

## 15. Rischi tecnici

### Rischio principale: qualità delle fonti
Le sorgenti possono avere:
- contenuti non uniformi;
- dati incompleti;
- formato variabile;
- informazioni non aggiornate;
- licenze e robots non chiari.

### Rischio secondario: deduplicazione
Eventi simili ma non identici possono essere confusi. È necessario un modello di score con review umana per casi ambigui.

### Rischio geocodifica
Indirizzi incompleti, luoghi non standard, CAP errati, nomi non univoci. Serve cache e validazione.

### Rischio sul modello temporale
Eventi con più date, weekend, ricorrenze e aperture straordinarie richiedono una rappresentazione data più sofisticata di un semplice `start_date/end_date`.

### Rischio di pubblicazione prematura
Non si deve pubblicare un evento senza abbastanza informazioni di base: titolo, data, luogo, confidenza minima, sorgente verificata.

### Rischio SEO e content quality
Pagine generate senza testo, senza contesto locale e senza schema non hanno valore.

---

## 16. Funzionalità da lasciare fuori dall’MVP

- Organizzami la giornata
- Sorprendimi
- Eventi vicini avanzati con routing stradale
- Area utenti organizzatori completa
- Payment / sponsorizzazione
- AI extraction come requisito per tutti i parser
- Elasticsearch/OpenSearch
- login social e account estesi
- grandi sistemi di analytics complessi
- feature monetizzazione avanzata
- routing stradale integrato

Le funzionalità sopra possono essere progettate, ma non devono essere implementate nel primo ciclo in modo da non sacrificare la solidità del nucleo.

---

## 17. Roadmap dettagliata

### Fase 0 — Analisi
- definizione requisiti e priorità
- verifica delle tecnologie
- critiche e decisioni architetturali
- schematico database
- fonti iniziali e valutazione di rischio

### Fase 1 — Fondazioni
- monorepo
- Next.js
- FastAPI
- PostgreSQL/PostGIS
- Docker Compose
- ambienti dev/staging/prod
- health checks
- migration system

### Fase 2 — Database
- schemi principali
- tabelle geografiche italiane
- località, comuni, province, regioni
- dati iniziali e indici geospaziali

### Fase 3 — MVP frontend
- homepage con ricerca
- mappa Italia
- clustering e marker
- lista eventi
- filtro per data e categorie
- pagina evento con fonte
- responsività mobile
- dati demo

### Fase 4 — Prima fonte reale
- scegli una fonte affidabile e verificata
- fetch + parse + normalize + geocode + deduplicate + save + publish
- monitorare output e alert

### Fase 5 — Più fonti
- regioni e comuni selezionati
- Ticketmaster/portali turistici
- musei e teatri
- Pro Loco

### Fase 6 — Admin
- dashboard
- verifiche eventi
- eliminazione logica
- gestione fonti e log
- revisione manuale

### Fase 7 — Automazione
- scheduler
- reimport
- alert per crawler rotti
- compare date e cancellazioni
- audit trail

### Fase 8 — SEO
- sitemap, metadata, JSON-LD, pagine territoriali

### Fase 9 — Funzioni gita
- weekend
- eventi vicini
- sorprendi
- raggruppamento per destinazione

---

## 18. Ordine esatto consigliato per lo sviluppo

1. Documentazione e decisioni architetturali
2. Setup monorepo + container di sviluppo
3. Database PostgreSQL/PostGIS + migrazioni
4. Modello dati base e geografie italiane
5. API CRUD e health checks
6. MVP frontend home + mappa + lista + filtri base
7. Pagina dettaglio evento + SEO base
8. Fonte reale 1: comune / regione / evento ufficiale verificato
9. Pipeline di fetch + parse + normalize + validate + save
10. Geocoding + cache + deduplication base
11. Admin dashboard base
12. Integrazione di una seconda fonte
13. Monitoraggio, alert e job schedulati
14. SEO avanzato e pagine territoriali
15. Estensioni future: weekend, vicini, sorprendi

Questo ordine minimizza il rischio di costruire un frontend bello ma senza un backend di ingestione affidabile.

---

## 19. Decisioni di progetto migliori per questo MVP

### Priorità assoluta
1. affidabilità dei dati;
2. pipeline di importazione controllata;
3. deduplicazione;
4. geocodifica con cache;
5. ricerca geospaziale reale;
6. pagina evento con provenienza chiara;
7. mappa utile e navigabile.

### Decisioni in linea con il brief
- usare PostgreSQL + PostGIS davvero, non solo per il salvataggio di coordinate;
- mantenere separato raw data e normalized event;
- usare `EventSource` e `EventOccurrence` per supportare ricorrenze e casi complessi;
- progettare provider intercambiabili per mappe e geocodifica;
- non usare AI come soluzione predefinita; solo come supporto per contenuti non strutturati;
- iniziare con alcune fonti selezionate e affidabili, non con centinaia di scrapers senza controllo.

---

## 20. Conclusione

L’idea centrale del progetto è valida e molto interessante, ma il vero punto di forza non è la mappa: è la capacità di costruire una pipeline di dati affidabile per eventi italiani, con deduplicazione, geocodifica, validazione e persistenza geografica. Solo così l’app può davvero rispondere alla domanda “dove posso andare oggi o questo weekend?” con risultati coerenti, utili e sostenibili nel tempo.

Il percorso consigliato è quindi progressivo, ma rigoroso: fondare la piattaforma su un modello dati solido, un sistema di importazione controllato, una geocodifica efficiente e una deduplicazione corretta. Dopo questa base, il frontend e la mappa diventeranno uno strumento davvero utile e non semplicemente un contenitore di marker.

---

## 21. Prime fonti consigliate come priorità reale per l’MVP

1. Comune di Roma - calendario eventi, manifestazioni, mostre, musei e iniziative culturali
2. Regione Lazio - eventi regionali e portali turistici
3. Ministero della Cultura / musei statali / portali culturali
4. IAT e enti turistici regionali
5. Pro Loco di comuni con eventi tradizionali e sagre
6. Ticketmaster Discovery  / grandi eventi musicali e festival
7. Comuni capoluogo di città con festival e fiere importanti

Questa lista è un buon primo nucleo per costruire una pipeline reale, verificabile e scalabile.
