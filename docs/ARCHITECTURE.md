# Architecture and implementation roadmap

## Product boundaries

The application has three independent primary experiences in the requested order: Kundli Chart, Palmistry, Combined Analysis. Supporting navigation opens working, clearly scoped views. Calculation services own numerical outputs; interpretation services may only describe outputs already produced and cite retrieved material.

## Request flow

1. Birth form validates required local birth time, IANA time zone, coordinates, and the selected calculation settings.
2. FastAPI converts local civil time to UTC with the historical transition rules in `zoneinfo`.
3. Swiss Ephemeris returns sidereal D1 longitudes and ascendant; settings and source inputs are stored with the result in MongoDB.
4. UI renders only returned values and labels unsupported modules.

Palm image intake and any future AI synthesis must be separate services. Image detection confidence must remain separate from user-corrected markings. AI must receive verified calculations plus retrieved, licensed reference material; it must never calculate chart positions or dates.

## MongoDB collection plan

`users`, `sessions`, `profiles`, `kundli_records`, `planetary_calculations`, `divisional_charts`, `dasha_records`, `palmistry_sessions`, `palm_images`, `palm_features`, `palm_reports`, `combined_reports`, `conversations`, `messages`, `knowledge_sources`, `knowledge_chunks`, `saved_reports`, and `user_preferences`. Profile-owned analysis records carry `owner_id`, `profile_id`, and timestamps. Current implementation writes `users`, hashed-token `sessions`, `profiles`, `kundli_records`, and `planetary_calculations`, and exposes owner-scoped profile and chart-history retrieval/deletion; the rest are indexed schema boundaries, not feature claims.

## Delivery sequence

1. Establish app shell, navigation, username/password accounts, signed sessions, per-user profile ownership, birth workflow, Mongo connection, and verifiable D1 output. **Current foundation.**
2. Add an optional user-held recovery-code flow, password change, shared-store auth rate limiting, and historical zone uncertainty display. Basic chart calculation history is implemented; historical time-zone uncertainty is still pending.
3. Validate ephemeris settings with cited reference cases; implement divisional chart conventions, Dashas, Panchang, strength, Ashtakavarga, and rule-by-rule yoga modules as separately reviewed calculation packages.
4. Build palm photo capture guidance, secure object storage, quality evaluation, human-correctable line annotations, and a validated detector before any interpretive report.
5. Add licensed source ingestion and provenance, retrieval, source citations, persisted conversations, and combined synthesis. A Gemini chat path is now available for selected D1 calculations; it does not claim classical-source citations until this phase is complete.
6. Add report export, resilient background jobs, admin/operations, observability, accessibility/responsive review, security review, and a documented repeatable validation suite before production.

No later phase should be labeled complete without its domain-specific validation and licensing review.
