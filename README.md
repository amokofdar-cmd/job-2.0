# job-2.0

An autonomous **job discovery + application orchestration** service with:

- Continuous job ingestion
- Resume/cover-letter tailoring
- OpenRouter multi-LLM failover routing
- Browser + API application channels
- Question memory with pause-on-unknown behavior
- Deduplication, safety controls, and audit logs

## Why this exists

Most job automation tools break on one of these:

- Limited ATS/site coverage
- No robust unknown-question handling
- No centralized application history
- No LLM failover strategy

This project provides a modular architecture so each weak point can be improved independently.

---

## Features

### 1) Autonomous search loop
Background worker keeps scanning registered sources, normalizes listings, deduplicates, and queues matches.

### 2) Match tiers
Jobs are scored into `A`, `B`, `C` tiers to blend direct-fit and adjacent opportunities.

### 3) LLM failover orchestration (OpenRouter)
`LLMRouter` accepts an ordered list of models and retries automatically. If one model fails or times out, it moves to the next.

### 4) Hybrid application strategy
- **API applicator** for stable endpoints
- **Browser applicator** fallback for dynamic ATS flows

### 5) Question memory
When a new form question appears:
- if known => auto-answer
- if unknown => mark as pending + requires human answer

### 6) Audit + safety
Every attempt gets an audit record and can be reviewed. Global run can be paused/resumed.

---

## Quickstart

### 1. Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### 2. Configure

Copy env and edit:

```bash
cp .env.example .env
```

Set:

- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL_CHAIN`

### 3. Run API

```bash
uvicorn app.main:app --reload
```

Open: <http://127.0.0.1:8000/docs>

### 4. Run autonomous worker

```bash
python -m app.workers.autopilot
```

---

## Architecture

- `app/main.py` FastAPI app + router registration
- `app/api/routes.py` HTTP endpoints
- `app/services/llm_router.py` OpenRouter failover + checkpointed prompt flow
- `app/services/matcher.py` scoring + tiers
- `app/services/applicator.py` API/browser application channels
- `app/services/question_memory.py` reusable Q&A memory
- `app/services/discovery.py` job source orchestrator
- `app/workers/autopilot.py` continuous loop
- `app/db/*` persistence and session management

---

## Notes

- This repository includes a production-style skeleton with working core logic.
- Platform-specific submitters (Ashby/Greenhouse/Workday/LinkedIn) are represented through adapters and should be expanded with each site’s approved integration path.
- Keep all candidate data truthful and policy-compliant.
