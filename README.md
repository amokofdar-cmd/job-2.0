# job-2.0

A full-stack autonomous job discovery + application orchestration app.

## What is now fully testable

After starting the backend, you can open a complete UI at:

- **`/app`** — no frontend build step required

From that UI, you can:

- seed demo data,
- create profiles,
- add jobs,
- score jobs,
- apply jobs,
- run autopilot once,
- manage question memory,
- monitor attempts and metrics.

---

## Backend run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload
```

Open:

- Full app UI: <http://127.0.0.1:8000/app>
- API docs: <http://127.0.0.1:8000/docs>

---

## Included clients

- `app/static/` — full working browser UI served directly by FastAPI
- `web/` — React + Vite operator console (optional)
- `mobile/` — Expo React Native console (optional)

---

## Core endpoints

- `POST /v1/profiles`
- `GET /v1/profiles`
- `POST /v1/jobs`
- `GET /v1/jobs`
- `POST /v1/jobs/{job_id}/score`
- `POST /v1/jobs/{job_id}/apply`
- `POST /v1/drafts`
- `POST /v1/questions`
- `POST /v1/questions/lookup`
- `GET /v1/attempts`
- `GET /v1/dashboard/metrics`
- `POST /v1/autopilot/run-once`
- `GET/PATCH /v1/run-control`
- `POST /v1/dev/seed-demo`

---

## OpenRouter failover

Set in `.env`:

```env
OPENROUTER_MODEL_CHAIN=model-a:free,model-b:free,model-c:free
```

The router attempts each model in order until one succeeds.
