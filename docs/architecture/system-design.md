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

12. GEO subsystem implementation (aligned with geo.md)
12.1 Data acquisition strategy (SERP/Exa first, optional light page fetch)
- External signals (no in-house crawling required):
  - SERP API: SERP features, PAA, competitive URLs, (optionally) AI Overviews if provider supports
  - Exa API: cross-site search/crawl for third-party mentions, directory listings, news; provides evidence URLs
  - PageSpeed Insights API: CWV/perf per URL (mobile/desktop)
  - Google Search Console (optional): impressions/clicks/CTR/avg position ground truth
- Internal limited access (recommended):
  - Fetch sitemap.xml → pick Top N important URLs (e.g., 50/100) by sitemap + GSC
  - For these URLs, fetch HTML (optionally headless render for JS-injected schema) and extract:
    - Schema types (FAQ/HowTo/LocalBusiness/Product/Article), meta/canonical/hreflang/status
    - Headings hierarchy (H1–H3), list/table density, Q&A blocks, paragraph lengths
    - Basic internal links (local graph signal)
- Configurable modes:
  - no_crawl: only SERP/Exa/PSI/GSC
  - sample_fetch(n): limited page sampling (recommended baseline)
  - shallow_crawl(depth, max_pages): optional upgrade for link graph/orphan/404 scan

12.2 GEO agents
- EntityAgent: map Organization/Person/Product/LocalBusiness to external KGs (Wikidata/Google KG), produce schema diff/checklist and missing fields
- ContentStructAgent: compute extractability score for Top N pages (headings_ok, faq_count, list/table density, qna_blocks, avg_paragraph_len)
- CitationAgent: analyze outbound/inbound citations; suggest authoritative references to back claims; track external citations (via Exa)
- SentimentAgent: monitor brand sentiment in sampled answers/articles; flag risky topics; suggest corrective content
- AIInterviewAgent (SERPSpy): generate GEO query templates (brand/core tasks/geo variants); sample AI answers if available; fallback to SERP+authority sources; tag confidence
- IntegratorNode: merge agent outputs and prioritize actions by Impact/Effort and KPI gaps

12.3 Orchestration (LangGraph)
- Parallel stage: run Entity/ContentStruct/Citation/Sentiment/AIInterview in parallel
- Debate stage: Advocate (opportunity) vs Reviewer (critique/completeness/compliance) rounds (max_debate_rounds)
- Risk stage: rotate technical risk (perf/rollback/compat), brand/compliance (E-E-A-T/citations/entity consistency), implementation complexity (cost/deps/teams) (max_risk_rounds)
- Final decision: produce action_plan with structured tasks (action/area/impact/effort/owner/deps)

12.4 GEO KPIs
- presence_rate: brand presence in AI answers for target queries
- snippet_ownership_score (SOS): fraction of snippets attributable to your content
- citations_count & authority: external citations (quantity/authority/trust)
- sentiment_ratio: positive/neutral/negative distribution
- zero_click_presence: AI summary presence vs traditional clicks
- schema_coverage: % of key pages with correct schema
- extractability_score: page-level extractability metric
- freshness & NAP consistency: content recency; local NAP intra-site consistency

12.5 API contracts (REST + Realtime)
- POST /geo/analyze
  - body: { version: "v1", site_id: uuid, mode: "no_crawl" | "sample_fetch", providers: { serp?: boolean, exa?: boolean, psi?: boolean, gsc?: boolean }, sample_size?: number }
  - return: { run_id: uuid }
- GET /geo/runs/{run_id}
  - return: { status: "queued"|"running"|"completed"|"failed", progress: number (0-100), outputs_summary?: {...} }
- GET /geo/plan/{run_id}
  - return: { items: [{ action, area: "entity"|"content"|"citation"|"sentiment"|"geo_local", impact: 1-5, effort: 1-5, owner?: string, deps?: string[] }] }
- GET /geo/kpis?site_id&from&to
  - return: { presence_rate_ts: [...], sos_ts: [...], citations_ts: [...], sentiment_ts: [...] }
- WS/SSE /ws/geo/runs/{run_id}
  - events: { stage, status, percent_complete, message? }

12.6 Supabase schema (DDL draft)
Note: add tenant_id uuid to all tables; enable RLS; policies match tenant_id from JWT.

```sql
-- Entities and extractability
create table if not exists geo_entities (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  site_id uuid not null,
  entity_type text not null, -- Organization | Person | Product | LocalBusiness
  name text not null,
  kg_id text,
  confidence numeric,
  last_seen timestamptz default now()
);
create index if not exists idx_geo_entities_site on geo_entities(site_id);

create table if not exists geo_extractability (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  site_id uuid not null,
  url text not null,
  headings_ok boolean,
  faq_count int default 0,
  table_count int default 0,
  list_density numeric,
  qna_blocks int default 0,
  avg_paragraph_len numeric,
  updated_at timestamptz default now()
);
create index if not exists idx_geo_extractability_site_url on geo_extractability(site_id, url);

-- AI answers sampling & citations
create table if not exists ai_answers (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  site_id uuid not null,
  ts timestamptz not null default now(),
  platform text not null, -- google_ai_overviews | chatgpt | perplexity | etc
  query text not null,
  present boolean not null,
  snippet text,
  citations jsonb,
  sentiment text -- positive | neutral | negative
);
create index if not exists idx_ai_answers_site_ts on ai_answers(site_id, ts desc);

create table if not exists geo_citations (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  site_id uuid not null,
  url text not null,
  cited_by text not null,
  authority_score numeric,
  last_seen timestamptz default now()
);
create index if not exists idx_geo_citations_site_url on geo_citations(site_id, url);

-- NAP audit for local GEO
create table if not exists nap_audit (
  id uuid primary key default gen_random_uuid(),
  tenant_id uuid not null,
  site_id uuid not null,
  location_id text,
  fields_ok boolean,
  inconsistencies jsonb,
  updated_at timestamptz default now()
);

-- RLS (example; adjust policy function per your JWT claims)
alter table geo_entities enable row level security;
create policy geo_entities_tenant_select on geo_entities for select
  using (tenant_id = (auth.jwt() ->> 'tenant_id')::uuid);
-- Repeat RLS enable/policies for all tables
```

12.7 Evaluation & reflection
- LLM-as-a-Judge: score evidence sufficiency, extractability, structure completeness, brand safety
- Ground Truth: GSC/PSI trends, (if available) AI summary citations traffic
- Fact checks: schema validity, citation validity, NAP consistency, FAQ/HowTo effectiveness
- Reflection memory: write "context-action-result-learning" rows (use pgvector or JSONB) grouped by role/topic for future retrieval

12.8 Rollout plan (GEO)
- Phase 1: SERP+Exa+PSI only, no page fetch; produce external-visibility plan with confidence labels
- Phase 2 (recommended baseline): add sitemap fetch + Top N page sampling; unlock schema/extractability/NAP checks
- Phase 3: optional shallow crawl (depth 1–2) for link graph/orphans/broken links
- Phase 4: enterprise sites: integrate third-party crawlers or full-scan pipeline

