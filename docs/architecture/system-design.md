# System Design: SEO + GEO Multi-Agent Platform

Purpose
- Provide concrete design choices for API style, frontend/backend split, database on Supabase, async orchestration, observability, and an MVP path.
- This complements project-overview.md by focusing on runtime architecture and trade-offs.

1. Interface style: REST vs alternatives
A. Recommended baseline (hybrid)
- REST control-plane API for commands and retrieval
  - POST /sites, POST /analyze, GET /runs/{id}, GET /plans/{id}, GET /kpis
- Async job processing for long-running workflows (LangGraph orchestrations)
- Realtime updates via:
  - WebSocket (FastAPI/Starlette) or
  - Supabase Realtime (Postgres logical replication) on runs/status tables
- Optional webhooks for external system notifications
Rationale
- Simple to integrate, cache-friendly, debuggable. REST suits command/query surfaces; realtime channel covers progress streaming without polling.

B. When to consider GraphQL
- If the frontend needs flexible aggregation over many entities (sites, runs, insights, tasks) with under/over-fetching concerns
- Unified schema with type safety and client-side codegen
Trade-offs: higher infra and schema governance cost; defer until UI complexity justifies it.

C. When to consider gRPC (internal only)
- If splitting into multiple backend services (orchestrator, crawler, evaluator) with high-throughput internal RPC
- Keep public API as REST; gRPC for service-to-service only

2. Backend design
A. Services and responsibilities
- API Service (FastAPI): authentication, REST endpoints, request validation, serving read models, websocket endpoints
- Orchestrator Service (LangGraph): executes SEO/GEO graphs, schedules agent runs, writes progress and results
- Worker/Queue: background jobs (Celery+Redis or RQ/Arq). For MVP, FastAPI BackgroundTasks is acceptable; plan upgrade to Celery when concurrency grows
- Artifact Storage: Supabase Storage (crawl JSON, lighthouse reports), or S3-compatible bucket

B. Core endpoints (initial)
- POST /analyze { url, locale?, site_id? } -> { run_id }
- GET /runs/{run_id} -> { status, progress, outputs_summary }
- GET /runs/{run_id}/logs -> stream or paginated logs
- GET /sites/{id}/kpis?from&to -> KPI time series (GSC, CWV, AI mentions)
- GET /plans/{run_id} -> optimization plan (actions with impact/effort)
- POST /webhooks/sink (optional) -> receive third-party callbacks

C. Orchestration model
- Write a Run row on POST /analyze (status=pending)
- Enqueue job -> Orchestrator loads SEOState, executes nodes in parallel/sequence
- Persist node outputs to insights tables (keyword/content/tech/geo/link)
- Update Run status and percent_complete; publish realtime events
- On completion, synthesize action_plan and KPI deltas

3. Frontend design
A. Stack
- Next.js or any SPA/SSR framework
- Supabase Auth for login (GitHub/Email OTP), JWT forwarded to backend
- Supabase Realtime to subscribe to runs/status updates (or WebSocket from API service)

B. UI surfaces (MVP)
- Sites: register and manage target sites
- Analyze: trigger a run, show live progress, node timings, costs
- Insights: per-run results across keyword/content/tech/geo/link
- Plan: impact/effort sorted tasks; export YAML/CSV
- KPIs: time series dashboard (GSC/GMB/CWV/AI mentions)

4. Database (Supabase/Postgres)
A. Entities (proposed)
- tenants(id, name)
- users(id, email, tenant_id)
- sites(id, tenant_id, url, locale)
- runs(id, site_id, created_at, status, progress, started_at, finished_at, error)
- insights_keyword(run_id, data jsonb)
- insights_content(run_id, data jsonb)
- insights_technical(run_id, data jsonb)
- insights_geo(run_id, data jsonb)
- insights_link(run_id, data jsonb)
- action_plans(run_id, items jsonb)  -- [{action, area, impact, effort, owner?, deps?}]
- kpi_snapshots(site_id, ts, gsc jsonb, cwv jsonb, ai jsonb, gmb jsonb)
- ai_mentions(site_id, ts, platform, query, sentiment, sources jsonb)
- citations(site_id, url, cited_by, authority_score, last_seen)

B. Indexing & Realtime
- Index runs(site_id, created_at desc), runs(status)
- Realtime on runs and action_plans for UI live updates

C. Security
- RLS per tenant_id on all tables
- Service key used by backend; end-user queries via RLS policies

D. Storage
- Use Supabase Storage bucket: crawls/, reports/, screenshots/; store paths in runs or artifacts table

5. Observability and cost
- Tracing: LangSmith (graphs, node timings), OpenTelemetry for API/worker
- Logs: structured JSON (run_id, node, duration_ms, tokens_in/out, cost)
- Metrics: runs.started/finished, success_rate, p95 durations, token/cost budgets
- Cost controls: model-tier routing (deep vs quick), sampling, cap max rounds, page limits

6. Deployment topologies
- MVP (simple):
  - Frontend: Vercel/Netlify
  - Backend: Render/Fly.io (single container)
  - Queue: Upstash Redis or managed Redis
  - Database/Storage/Auth: Supabase Cloud
- Scale-out (later):
  - API, Orchestrator workers, and Headless crawler split into services
  - Private networking among services; gRPC internal if needed

7. REST vs others: explicit recommendation
- Start with REST + Realtime (WebSocket or Supabase Realtime). This is sufficient and lowest friction
- Revisit GraphQL once UI needs cross-entity aggregation and client-side composition
- Keep gRPC for internal microservices only when you actually split services

8. Data contracts and schemas
- All public JSON payloads versioned: { version: "v1", ... }
- JSON Schema for request/response validation (pydantic models)
- For large artifacts, return signed URLs instead of inlining

9. Security & tenancy
- Supabase Auth (JWT) -> tenant resolution
- RLS on all data; admin service key only on server side
- Per-tenant rate limits and cost budgets; alerting on threshold breach

10. MVP execution plan (sequenced)
1) Provision Supabase (auth, db, storage). Create schema and RLS
2) Implement REST API (POST /analyze, GET /runs/{id}) + BackgroundTasks executor
3) Implement Orchestrator happy-path (crawl + parallel agents + integration)
4) Persist insights/action_plan; publish Realtime events
5) Build minimal UI: create site, trigger run, live progress, show plan
6) Add KPIs ingest (GSC/CWV) and dashboards; add retry/timeout; add logs
7) Introduce a real queue (Celery) and headless browser pool; secure secrets

11. Open questions for discussion
- Target concurrency and expected run duration per site?
- Prefer WebSocket vs Supabase Realtime for progress? (trade-off: ops vs latency)
- Which external data sources are in-scope for MVP? (GSC/Pagespeed mandatory; Ahrefs/Semrush optional)
- Multi-tenant isolation: single project multi-tenant vs per-tenant Supabase project?
- Frontend framework preference (Next.js assumed) and hosting choice?

Appendix: Pros/Cons snapshot
- REST+Realtime: +simple +debuggable +CDN friendly; -manual joins client-side
- GraphQL: +flexible queries +single roundtrip; -added complexity/schema ops
- gRPC: +fast internal RPC; -browser unfriendly, not for public API

