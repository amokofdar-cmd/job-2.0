# job-2.0

A full-stack autonomous job application platform with:

- FastAPI backend API
- Continuous autopilot worker
- **Built-in web UI served directly by FastAPI** (no Node required)
- Optional React web console (`web/`)
- Optional Expo mobile console (`mobile/`)
- OpenRouter model failover routing
- Question memory, scoring tiers, and hybrid apply adapters

---

## 1) Quick test (fastest path)

This gives you a working app UI quickly.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload
```

Open: `http://127.0.0.1:8000/`

Then in UI:
1. Click **Seed Demo Data**
2. Click **Run Autopilot Once**
3. Inspect Jobs, Attempts, and Metrics updating

Health endpoint: `http://127.0.0.1:8000/health`

---

## 2) Core backend capabilities

- Profiles CRUD-lite (`create/list`)
- Job ingestion + listing filters
- Tier scoring endpoint
- LLM-based draft generation with OpenRouter failover chain
- Question memory save + lookup
- Apply endpoint with hybrid API/browser adapter abstraction
- Run control (pause/resume)
- Metrics + attempts history
- Demo bootstrap endpoint for one-click local validation

### Main endpoints

- `POST /v1/bootstrap/demo`
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

## 3) Built-in UI screens

The built-in FastAPI-hosted UI (`app/ui/*`) includes:

- Metrics cards
- Profile creation form
- Job creation form
- Job filtering + per-job actions (score/apply)
- Attempts table
- Question memory save + lookup
- Demo seed + autopilot run controls

---

## 4) Optional separate web app (`web/`)

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

## 5) Optional mobile app (`mobile/`)

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

## 6) OpenRouter configuration

Set in `.env`:

```env
OPENROUTER_API_KEY=...
OPENROUTER_MODEL_CHAIN=model-a:free,model-b:free,model-c:free
```

`LLMRouter` retries models in order and uses the first successful response.

---

## 7) Notes

- This repo is now runnable as a complete app via FastAPI + built-in UI.
- ATS adapters in `app/services/applicator.py` remain modular to implement provider-specific logic (Ashby/Greenhouse/Workday/LinkedIn/etc.).
- Keep candidate claims truthful and policy-compliant.
