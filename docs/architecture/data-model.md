# Data Model and RLS (Supabase)

This document describes the initial relational schema for Supabase (Postgres), indexes, and row-level security (RLS) guidance. It is cost-first and suitable for MVP with mock data.

Notes
- All tables include tenant_id for multi-tenant isolation
- Use JSONB for flexible payloads (insights) to reduce early migrations
- Create minimal indexes that directly serve primary reads
- Enable RLS on all tables; only API/Worker with service role bypass RLS

Core tables (MVP)
- tenants(id, name)
- users(id, email, tenant_id)
- sites(id, tenant_id, url, locale)
- runs(id, site_id, created_at, status, progress, error, started_at, finished_at)
- insights_keyword(run_id, data jsonb)
- insights_content(run_id, data jsonb)
- insights_technical(run_id, data jsonb)
- insights_geo(run_id, data jsonb)
- insights_link(run_id, data jsonb)
- action_plans(run_id, items jsonb)
- kpi_snapshots(site_id, ts, gsc jsonb, cwv jsonb, ai jsonb, gmb jsonb)
- ai_answers(site_id, ts, platform, query, present, snippet, citations jsonb, sentiment)
- geo_entities(site_id, entity_type, name, kg_id, confidence)
- geo_extractability(site_id, url, headings_ok, faq_count, table_count, list_density, qna_blocks, avg_paragraph_len)
- geo_citations(site_id, url, cited_by, authority_score, last_seen)
- nap_audit(site_id, location_id, fields_ok, inconsistencies jsonb)

DDL draft (Postgres)
- Use gen_random_uuid() from pgcrypto
- Example DDL snippets are in system-design.md §12.6; below we add core MVP tables

Indexes (cost-first)
- runs(site_id, created_at desc), runs(status)
- ai_answers(site_id, ts desc)
- geo_extractability(site_id, url)
- action_plans(run_id)
- insights_* (run_id)

RLS strategy (practical guide)
- All business tables: enable RLS
- Client traffic: only via API; API attaches Supabase JWT that contains tenant_id
- Policies:
  - SELECT: tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
  - INSERT: tenant_id = (auth.jwt() ->> 'tenant_id')::uuid AND FK belongs to same tenant
  - UPDATE/DELETE: same as SELECT + ownership checks if needed
- Service role (API/Worker): uses service key; bypasses RLS for system writes (e.g., workers persisting insights)

Example policies (per table)
```sql
alter table runs enable row level security;
create policy runs_select on runs for select using (
  tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
);
create policy runs_insert on runs for insert with check (
  tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
);
create policy runs_update on runs for update using (
  tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
);

alter table action_plans enable row level security;
create policy action_plans_select on action_plans for select using (
  tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
);
create policy action_plans_insert on action_plans for insert with check (
  tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
);
```

Best practices
- Do not expose direct client writes for insights_* and runs; only API/Worker should write them with service role
- For client-created resources (sites), allow INSERT with tenant_id from JWT and validate ownership in API
- Keep RLS minimal and explicit to avoid surprises; test policies with supabase CLI

