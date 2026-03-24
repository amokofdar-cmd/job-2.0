# job-2.0

A full-stack autonomous job application system with:

- FastAPI backend + SQLite persistence
- Autonomous worker loop
- OpenRouter multi-model failover routing
- Built-in browser UI served by backend (`/ui`) for no-build quick testing
- React web app (`web/`) and Expo mobile app (`mobile/`)

---

## Quick test (fastest path)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
python scripts/seed_demo.py
uvicorn app.main:app --reload
```

Then open:

- API docs: `http://127.0.0.1:8000/docs`
- Full built-in UI: `http://127.0.0.1:8000/ui`

From `/ui` you can:

- create candidate profiles
- add jobs
- run autopilot once
- manually apply by profile/job ID
- save reusable form Q&A
- inspect metrics + attempts

---

## Backend structure

- `app/main.py` app startup + CORS + static UI hosting
- `app/api/routes.py` API endpoints
- `app/models/entities.py` SQLAlchemy models
- `app/services/` matcher, analytics, llm router, question memory, applicator
- `app/workers/autopilot.py` continuous autonomous loop
- `scripts/seed_demo.py` test data bootstrap

### Main API endpoints

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

## Built-in backend UI (`app/ui/`)

No Node install required.

- `app/ui/index.html`
- `app/ui/styles.css`
- `app/ui/app.js`

Served automatically from FastAPI at `/ui` and `/ui-static/*`.

---

## React web app (`web/`)

```bash
cd web
npm install
npm run dev
```

Set optional API base:

```bash
VITE_API_BASE=http://127.0.0.1:8000/v1
```

---

## Mobile app (`mobile/`)

```bash
cd mobile
npm install
npm run start
```

Set optional API base:

```bash
EXPO_PUBLIC_API_BASE=http://127.0.0.1:8000/v1
```

---

## OpenRouter failover

Configure in `.env`:

```env
OPENROUTER_MODEL_CHAIN=model-a:free,model-b:free,model-c:free
```

The router tries models in order and fails over automatically.

---

## Notes

- This repo now includes a directly testable UI at `/ui` plus separate web/mobile clients.
- ATS-specific submission/discovery adapters are structured for extension per platform.
