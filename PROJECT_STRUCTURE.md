# Project structure (scaffold)

api/                  # FastAPI app (REST + WS/SSE)
workers/              # Orchestrator & background jobs (Celery/RQ)
agents/               # Domain agents (keyword/content/technical/geo/link)
  keyword/
  content/
  technical/
  geo/
  link/
graph/                # LangGraph nodes/edges orchestration
services/             # Integrations (SERP/Exa/PSI/GSC/Storage)
schemas/              # Pydantic schemas (request/response)
models/               # Persistence models / SQL helpers
scripts/              # Utilities (DB migrations, mock import)
mock-data/            # Seed data (CSV/JSON)
tests/                # Unit/integration tests

README.md             # Repo overview
WARP.md               # Warp guidance (already present)
docs/                 # Documentation (already structured)

