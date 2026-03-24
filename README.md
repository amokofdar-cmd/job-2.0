# job-2.0

An autonomous **job discovery + application orchestration platform** with:

- Backend API + autonomous worker
- OpenRouter multi-LLM failover generation
- Web operator console
- Mobile operator console
- Question memory with human-in-the-loop fallback
- Hybrid apply channels (API + browser adapters)

## Monorepo layout

- `app/` Python backend (FastAPI + SQLAlchemy + worker)
- `web/` React + Vite dashboard
- `mobile/` Expo React Native app
- `tests/` backend tests

---

## Backend

### Features

- Candidate, job, application-attempt, and run-control persistence
- Job scoring (`A/B/C` tiers)
- OpenRouter failover model chain
- Tailored draft generation endpoint
- Question memory lookup/save for form autofill
- Manual and autonomous apply workflows
- Dashboard metrics + attempts history

### Run backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload
```

### Run autonomous loop

```bash
python -m app.workers.autopilot
```

API docs: <http://127.0.0.1:8000/docs>

---

## Web app (`web/`)

### Features

- Dashboard metrics cards
- Job table view
- Trigger `autopilot/run-once` from UI

### Run web

```bash
cd web
npm install
npm run dev
```

Optional env:

```bash
VITE_API_BASE=http://127.0.0.1:8000/v1
```

---

## Mobile app (`mobile/`)

### Features

- Dashboard metrics view
- Jobs feed
- Trigger autopilot run
- Open job links externally

### Run mobile

```bash
cd mobile
npm install
npm run start
```

Optional env:

```bash
EXPO_PUBLIC_API_BASE=http://127.0.0.1:8000/v1
```

---

## Core API endpoints

- `POST /v1/profiles`
- `GET /v1/profiles`
- `POST /v1/jobs`
- `GET /v1/jobs`
- `POST /v1/jobs/{job_id}/score`
- `POST /v1/drafts`
- `POST /v1/questions`
- `POST /v1/questions/lookup`
- `POST /v1/jobs/{job_id}/apply`
- `GET /v1/attempts`
- `GET /v1/dashboard/metrics`
- `GET/PATCH /v1/run-control`
- `POST /v1/autopilot/run-once`

---

## OpenRouter failover

Set in `.env`:

```env
OPENROUTER_MODEL_CHAIN=model-a:free,model-b:free,model-c:free
```

Router tries models in order and returns first successful completion.

---

## Notes

- This is a complete full-stack baseline with production-oriented structure.
- ATS-specific adapters (Ashby/Greenhouse/Lever/Workday/LinkedIn) should be implemented in `app/services/applicator.py` and discovery sources.
- Keep all candidate claims truthful and policy-compliant.
