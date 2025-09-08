# Workers (Orchestrator & Jobs)

Purpose
- Execute LangGraph workflows
- Call SERP/Exa/PSI/GSC providers
- Persist insights/action plans to Supabase

Notes
- Use Celery + Redis or similar
- Enforce rate limits and retries with exponential backoff

