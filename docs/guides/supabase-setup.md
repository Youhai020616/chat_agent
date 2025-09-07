# Supabase Setup (Cloud) with Mock Data

Goal
- Provision Supabase (Auth, DB, Storage), create schema with RLS, and load mock data for local testing.
- Cost-first: minimal indexes, JSONB payloads, limited realtime usage.

Prerequisites
- Supabase project (org dashboard)
- supabase CLI installed (optional but recommended)

1) Enable extensions
```sql
create extension if not exists pgcrypto; -- for gen_random_uuid()
```

2) Create core tables
- See docs/architecture/system-design.md §12.6 and docs/architecture/data-model.md
- Apply the DDL snippets via SQL editor. Ensure every table has tenant_id uuid not null.

3) Enable RLS and policies
- For each table:
```sql
alter table <table> enable row level security;
create policy <table>_select on <table> for select using (
  tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
);
create policy <table>_insert on <table> for insert with check (
  tenant_id = (auth.jwt() ->> 'tenant_id')::uuid
);
-- add update/delete as needed
```
- API/Worker will use service role key for system writes and bypass RLS.

4) Create Storage buckets
- buckets: crawls, reports, screenshots
- Restrict public access; API generates signed URLs as needed.

5) Load mock data
- Use Table Editor import or psql COPY.
- Files under mock-data/:
  - tenants.csv, users.csv, sites.csv
  - runs.csv, ai_answers.csv, geo_entities.csv, geo_extractability.csv, geo_citations.csv, nap_audit.csv
  - action_plans.json (array of items per run)
  - kpi_snapshots.csv (denormalized KPI for dashboards)

Example COPY (adjust schema/table as needed)
```sql
copy tenants(id, name) from stdin csv header;
```

6) Realtime (optional for cost)
- Start with API WebSocket/SSE for progress to avoid WAL noise
- If using Supabase Realtime on runs/action_plans, publish only coarse state changes

7) Secrets & roles
- Store service_role key server-side only
- End-user traffic uses anon key + RLS; never expose service key to clients

8) Next steps
- Wire API/Worker to Supabase using service role
- Add periodic KPI aggregation jobs if needed

