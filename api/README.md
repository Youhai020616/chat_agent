# API service (FastAPI)

Purpose
- Expose REST endpoints (POST /analyze, GET /runs/{id}, GET /plans/{run_id}, GET /kpis)
- Provide WS/SSE for progress updates
- Validate identity and map tenant_id from JWT

Notes
- Keep this service thin; heavy work happens in workers/
- Service role key used server-side only

