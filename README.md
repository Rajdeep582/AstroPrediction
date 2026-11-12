# Jyotish Studio

A Next.js web workspace with a FastAPI service. The first working path is a sidereal D1 calculation backed by Swiss Ephemeris and a MongoDB saved profile. Unsupported chart modules are marked as unavailable rather than filled with invented data.

## Project layout

```
AstroPrediction/
├── frontend/        Next.js 15 app (app/, components/, lib/, package.json) — port 4000
│   └── .env.local   NEXT_PUBLIC_* settings (API URL, site URL)
├── backend/         FastAPI service — port 8800
│   ├── app/         routes, calculation engine, MongoDB, field encryption
│   ├── run.py       entry point (auto-reload limited to backend/app)
│   ├── .venv/       isolated Python environment
│   └── .env         server secrets (MongoDB, encryption key, AI keys)
├── scripts/dev.mjs  starts backend + frontend together
└── docs/            architecture notes and archived code
```

## Run locally

First time: `npm run setup` (from the repository root).

- Both servers: `npm run dev` from the repository root → web http://localhost:4000, API http://localhost:8800/api/health
- Frontend only: `cd frontend` then `npm run dev`
- Backend only: `cd backend` then `.venv\Scripts\python run.py`

Run only one copy of each server. Atlas must allow this machine's IP under Network Access.

## Architecture

- `frontend/app/`: Next.js App Router UI; navigation, forms, accessible controls, and visual system.
- `backend/app/`: FastAPI validation, MongoDB connection/indexes, and isolated calculation service.
- `backend/app/astrology.py`: UTC conversion using IANA `zoneinfo`; sidereal D1 using Swiss Ephemeris. Planet houses are explicitly whole sign. Placidus sidereal cusps are retained as separate data.
- The public dashboard can be viewed without an account. Chart creation, saved profiles, chart history, palmistry workspace, combined analysis, AI assistance, reports, knowledge library, and settings require sign-in. The API enforces the same access rule; it does not create guest-owned data. Usernames are unique case-insensitively; MongoDB stores an Argon2 password hash, never an email or plaintext password. A random opaque session token is HTTP-only and SameSite=Lax; MongoDB stores only its SHA-256 hash and expires sessions after 14 days. Set `SESSION_HTTPS_ONLY=true` in HTTPS deployments. Username-only accounts have no recovery path and this remains a basic account flow, not a full production identity service.
- Kundli inputs, profiles, calculation records, and their latest chart history are persisted per user. The Saved Reports page reopens saved chart calculations. The AI assistant uses `AI_PROVIDER=gemini`, `GEMINI_API_KEY`, and `AI_MODEL`. For chart questions it sends the selected user's verified D1 placements and up to 10 recent chat messages; it omits profile identifiers and birth details. It does not yet have a licensed classical-source retrieval library, citations, or persisted AI conversations, and it will not invent those references or unsupported chart calculations.

## Calculation and licensing notes

The Swiss Ephemeris Python wrapper is listed on PyPI as AGPL-3.0, and Swiss Ephemeris itself is offered under AGPL or a Professional License. Review both license obligations and obtain the appropriate rights before distributing or operating a public service. Ephemeris data must also be supplied and licensed. Without data files, the application uses the library's built-in Moshier mode. An ayanamsa selection is applied to the supported D1 path.

Google Places Autocomplete and the draggable location map are available after setting a restricted `NEXT_PUBLIC_GOOGLE_MAPS_BROWSER_KEY`. Zero-key place search uses a deliberate single-result OpenStreetMap Nominatim request, not autocomplete, and includes request pacing, a small in-memory cache, and map attribution. Nominatim's public service is rate-limited and should be replaced with a self-hosted or commercial provider if application traffic grows; place text and reverse-geocoded coordinates are sent to the selected map provider. Time-zone lookup from coordinates is still manual. This release does not implement divisional charts, Dashas, Shadbala, Ashtakavarga, Yoga/Dosha evaluation, Panchang, historical time-zone ambiguity warnings, reference-grounded RAG, private image storage, palm computer vision, exports, or production administration. The interface identifies unavailable functions. It does not claim they have been calculated. Never use this local-development build as a public multi-user service.

## Data model plan

Indexes and collection boundaries are initialized in `backend/app/database.py` for users, profiles, Kundli calculations, divisional charts, Dashas, palm sessions/images/features/reports, combined reports, conversations/messages, knowledge sources/chunks, saved reports, and preferences. Implemented persistence covers users/sessions, profiles, Kundli records, planetary calculations, profile listing/deletion, and saved chart history. Palm image/report storage, AI conversation persistence, other analysis operations, retention policy, and migrations remain roadmap work.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the implementation sequence and workflow boundaries.
