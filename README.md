# LLM Usage Monitoring Service

FastAPI + Postgres backend, React/TS frontend. Fully Dockerized.

## Initial Commands for Project Setup 

```bash

cd <project-folder>
git clone <repository-url>
```
## Build & Run everything

```bash
docker compose up --build
```

## It will generate Backend Development Server at:

```bash
http://0.0.0.0:8000/docs
```

## It will also Generate frontend Dev Server at:
```bash
localhost:5173
```

## FastAPI auto-generates Swagger UI. You’ll see both endpoints:

```bash
POST /api/llm/chat

GET /api/usage/summary
```

# To run backend only
docker compose up backend

# run tests (inside container)
docker compose run --rm backend pytest -q

## Running frontend (dev)

Option A — run in Docker (recommended if you have Node version issues):

```bash
docker compose up frontend
# frontend is served via nginx; build container will use Node 20 image
```

Option B — run dev server locally:

```bash
cd frontend
# Ensure Node >= 18 (prefer 20). Use nvm: `nvm install 20 && nvm use 20`
npm install
npm run dev

it will run on localhost:5173

```
## Environment and Configuration 
Core environment variables used by the backend:
- `DATABASE_URL` — e.g. `postgresql+psycopg://postgres:postgres@db:5432/overmind`
- `OPENAI_API_BASE` — default `https://api.openai.com/v1` (set to a mock server when testing without quota)
- `PYTHONPATH` — set to `/app` in compose so tests can import `app` package

**To test with a real OpenAI key:** paste `sk-...` into the frontend form (OpenAI key only used to call the OpenAI API). Never commit keys.

If you see `crypto.getRandomValues is not a function`, upgrade Node or run inside Docker.
# run mock OpenAI server (local)
uvicorn mock_openai:app --port 9000 --reload

---

## Database schema & design (short)

Single primary table: `usage_logs`

Columns:

- `id` (pk)
- `created_at` (timestamp, default UTC)
- `user_label` (string) — application/business identifier for the caller (e.g., `alice`)
- `model` (string)
- `input_tokens` (int) — `usage.prompt_tokens` from OpenAI
- `output_tokens` (int) — `usage.completion_tokens` from OpenAI

**Why this design**

- Simple, normalized table that records each call with minimal metadata required for billing/monitoring queries.
- Aggregation is done with `GROUP BY model, user_label` in `/api/usage/summary` to show totals per user/model.

**Trade-offs**

- No per-organization table: assumes `user_label` suffices for multi-tenant labeling.
- No audit trail for request/response content to minimise sensitive storage.
- No migrations (Alembic) — schema auto-created at startup to keep the assessment lightweight. For production, add Alembic and explicit migrations.

---

## What I would add with more time

- **Alembic migrations** and stronger DB typing.
- **Auth & per-user API keys** (rotateable, scoped) instead of passing raw OpenAI keys via UI.
- **Rate limiting & quotas per user_label** to prevent abuse.
- **Better error & retry logic** for transient OpenAI failures (exponential backoff).
- Add **E2E tests** for the frontend (playwright) and richer unit coverage on backend.

---

## Troubleshooting ( Common issues )
- **`COPY nginx.conf` not found** — ensure `frontend/nginx.conf` exists in the repo. Create it if missing.
- **`ModuleNotFoundError: No module named 'app'` when running pytest** — add `PYTHONPATH: /app` to the backend service in `docker-compose.yml` or run pytest with `-e PYTHONPATH=/app`:
  ```bash
  docker compose run --rm -e PYTHONPATH=/app backend pytest -q
  ```
- **Vite error `crypto.getRandomValues is not a function`** — upgrade Node to >= 18 (Node 20 recommended) or run frontend in Docker.
- **OpenAI `insufficient_quota`** — means your account has no available quota. Use the mock server to test without spending credits, or top up billing.

## Helpful Commands Summary 

```bash
# build & run everything
docker compose up --build

# run backend only
docker compose up backend

# run tests (inside container)
docker compose run --rm backend pytest -q

# run frontend dev (local)
cd frontend
nvm install 20 && nvm use 20
npm install
npm run dev

# run mock OpenAI server (local)
uvicorn mock_openai:app --port 9000 --reload

```

