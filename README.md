# job-2.0

A full-stack autonomous job application platform with:

- FastAPI backend + autonomous worker
- OpenRouter multi-LLM failover routing
- Built-in browser UI served by backend (**no separate frontend install required**)
- Separate React web app (`web/`) and Expo mobile app (`mobile/`)

---

## Fastest way to test (single command flow)

1. Start backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
uvicorn app.main:app --reload
```

2. Open the full app UI:

- <http://127.0.0.1:8000/app>

3. Seed demo data from the UI by clicking **API Console** actions or via:

```bash
curl -X POST http://127.0.0.1:8000/v1/demo/seed
```

4. Use the UI to:
- create/select profile
- add jobs
- score/apply jobs
- run/pause autopilot
- save/lookup question memory
- inspect attempts + dashboard metrics

---

## Backend architecture (`app/`)

### Key routes

- `POST /v1/demo/seed`
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
- `GET/PATCH /v1/run-control`
- `POST /v1/autopilot/run-once`

### Full app UI routes

- `/app` main operator UI
- `/ui/static/*` assets (JS + CSS)

### Autonomous worker

```bash
python -m app.workers.autopilot
```

---

## Web app (`web/`) optional

```bash
cd web
npm install
npm run dev
```

Set API base (optional):

```bash
VITE_API_BASE=http://127.0.0.1:8000/v1
```

---

## Mobile app (`mobile/`) optional

```bash
cd mobile
npm install
npm run start
```

Set API base (optional):

```bash
EXPO_PUBLIC_API_BASE=http://127.0.0.1:8000/v1
```

---

## Notes

- This repo now includes a fully testable in-browser app served directly by FastAPI.
- Web and mobile clients consume the same API surface.
- Keep candidate claims truthful and policy-compliant.
