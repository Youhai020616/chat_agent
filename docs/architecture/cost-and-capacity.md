# Cost and Capacity Plan

Goals
- Keep infrastructure and vendor costs low at MVP
- Provide levers to scale only when necessary

Levers
- Sampling: limit Top N pages per site (50/100) for extractability checks
- Model routing: quick model for extraction, deep model only for final decisions
- Rate limiting: site/tenant/global quotas; exponential backoff and DLQ
- Realtime: use API WebSocket/SSE first; limit Supabase Realtime to coarse state changes
- Storage: store large artifacts in Storage buckets; DB stores paths only
- Index discipline: only add indexes proven to speed critical queries

Initial budgets (example)
- ai_answers sampling: <= 20 queries/day/site
- PSI calls: <= 20 urls/day/site (mobile only initially)
- Workers: 1-2 instances; autoscale off by default

Scale-up path
- Split worker roles (crawler vs orchestrator)
- Add Redis queue partitions and worker autoscaling based on queue length
- Add read replicas or materialized aggregates for dashboards

