# KPI Dashboard Rollout Plan (Cost-first)

Goal
- Deliver a practical, staged KPI dashboard aligned with GEO/SEO outcomes while controlling cost.

Principles
- Phase releases; start with metrics that require minimal external APIs
- Prefer daily aggregation and small time windows by default (last 7/28/90 days)
- Cache heavy queries with materialized views later

Phase 1 (Week 1-2)
- Data sources: runs, action_plans, ai_answers, kpi_snapshots (denormalized fields)
- Metrics
  - Runs: started, completed, success_rate, p95_duration (if measured)
  - GEO presence_rate (ai_answers.present true per query set / total sampled)
  - Sentiment ratio from ai_answers (pos/neu/neg)
  - Action plan throughput: actions per run, completion rate (if tracked)
- Example queries
```sql
-- presence_rate (last 28 days)
select date_trunc('day', ts) as day,
       avg(case when present then 1 else 0 end) as presence_rate
from ai_answers
where site_id = :site_id and ts >= now() - interval '28 days'
group by 1 order by 1;

-- sentiment ratio (last 28 days)
select date_trunc('day', ts) as day,
       avg(case when sentiment = 'positive' then 1 else 0 end) as pos,
       avg(case when sentiment = 'neutral' then 1 else 0 end) as neu,
       avg(case when sentiment = 'negative' then 1 else 0 end) as neg
from ai_answers
where site_id = :site_id and ts >= now() - interval '28 days'
group by 1 order by 1;
```

Phase 2 (Week 3-4)
- Add PageSpeed (CWV) and basic GSC fields in kpi_snapshots
- Metrics
  - CWV: avg LCP/CLS over tracked URLs
  - GSC: impressions, clicks, CTR trend, avg position (if GSC connected)
  - SOS (snippet_ownership proxy): share of answers citing your URLs (if available)
- Example queries
```sql
select date_trunc('day', ts) as day,
       (kpi->'cwv'->>'lcp')::numeric as lcp,
       (kpi->'cwv'->>'cls')::numeric as cls
from (
  select ts, jsonb_build_object(
    'cwv', jsonb_build_object('lcp', (kpi_snapshots.cwv->>'avg_lcp'), 'cls', (kpi_snapshots.cwv->>'avg_cls'))
  ) as kpi
  from kpi_snapshots
  where site_id = :site_id and ts >= now() - interval '28 days'
) t
order by day;
```

Phase 3 (Month 2+)
- Add citations authority (geo_citations), NAP consistency (nap_audit), extractability score (geo_extractability)
- Metrics
  - Authority trend (avg authority_score)
  - NAP issues count
  - Extractability index (avg of normalized features)
- Materialize
  - Create daily aggregates tables to keep dashboards fast and cheap

Cost control
- Limit sampling size of ai_answers per site per day
- Avoid high-cardinality dimensions; keep charts per site
- Use smaller default ranges; paginate raw tables

Tooling
- Grafana/Metabase on Postgres read; or lightweight in-app charts

