from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.entities import (
    ApplicationAttempt,
    CandidateProfile,
    JobListing,
    RunControl,
)
from app.schemas.common import (
    AnswerQuestionRequest,
    CandidateProfileCreate,
    GenerateDraftRequest,
    JobCreate,
    QuestionLookupRequest,
    RunControlUpdate,
)
from app.services.analytics import compute_dashboard_metrics
from app.services.applicator import HybridApplicator
from app.services.composer import DraftComposer
from app.services.llm_router import LLMRouter
from app.services.matcher import score_job
from app.services.question_memory import QuestionMemory
from app.workers.autopilot import run_cycle

router = APIRouter(prefix="/v1", tags=["job-automation"])


@router.post("/profiles")
def create_profile(payload: CandidateProfileCreate, db: Session = Depends(get_db)):
    profile = CandidateProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"id": profile.id}


@router.get("/profiles")
def list_profiles(db: Session = Depends(get_db)):
    items = db.execute(select(CandidateProfile).order_by(desc(CandidateProfile.id))).scalars().all()
    return [
        {
            "id": x.id,
            "full_name": x.full_name,
            "email": x.email,
            "linkedin_url": x.linkedin_url,
        }
        for x in items
    ]


@router.post("/jobs")
def upsert_job(payload: JobCreate, db: Session = Depends(get_db)):
    stmt = select(JobListing).where(JobListing.url == payload.url)
    existing = db.execute(stmt).scalar_one_or_none()
    if existing:
        return {"id": existing.id, "status": "exists"}

    job = JobListing(**payload.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return {"id": job.id, "status": "created"}


@router.get("/jobs")
def list_jobs(
    applied: bool | None = Query(default=None),
    tier: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    stmt = select(JobListing).order_by(desc(JobListing.id)).limit(limit)
    if applied is not None:
        stmt = stmt.where(JobListing.applied.is_(applied))
    if tier:
        stmt = stmt.where(JobListing.tier == tier)
    items = db.execute(stmt).scalars().all()
    return [
        {
            "id": x.id,
            "source": x.source,
            "company": x.company,
            "title": x.title,
            "location": x.location,
            "url": x.url,
            "tier": x.tier,
            "score": x.score,
            "applied": x.applied,
        }
        for x in items
    ]


@router.post("/jobs/{job_id}/score")
def score_job_endpoint(job_id: int, profile_id: int, db: Session = Depends(get_db)):
    job = db.get(JobListing, job_id)
    profile = db.get(CandidateProfile, profile_id)
    if not job or not profile:
        raise HTTPException(status_code=404, detail="job/profile not found")

    result = score_job(profile.master_resume, job.description)
    job.score = result.score
    job.tier = result.tier
    db.add(job)
    db.commit()
    return {"score": result.score, "tier": result.tier}


@router.post("/questions")
def save_question_answer(payload: AnswerQuestionRequest, db: Session = Depends(get_db)):
    qm = QuestionMemory(db)
    item = qm.save(payload.question_text, payload.answer_text, payload.approved)
    return {"id": item.id, "question_key": item.question_key}


@router.post("/questions/lookup")
def lookup_question(payload: QuestionLookupRequest, db: Session = Depends(get_db)):
    found = QuestionMemory(db).lookup(payload.question_text)
    if not found:
        return {"found": False}
    return {
        "found": True,
        "answer": found.answer_text,
        "approved": found.approved,
        "question_key": found.question_key,
    }


@router.post("/drafts")
async def generate_draft(payload: GenerateDraftRequest, db: Session = Depends(get_db)):
    profile = db.get(CandidateProfile, payload.profile_id)
    job = db.get(JobListing, payload.job_id)
    if not profile or not job:
        raise HTTPException(status_code=404, detail="job/profile not found")

    settings = get_settings()
    composer = DraftComposer(
        llm_router=LLMRouter(
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            models=settings.openrouter_model_chain,
        )
    )
    return await composer.compose(profile, job)


@router.post("/jobs/{job_id}/apply")
async def apply_job(job_id: int, profile_id: int, db: Session = Depends(get_db)):
    job = db.get(JobListing, job_id)
    profile = db.get(CandidateProfile, profile_id)
    if not job or not profile:
        raise HTTPException(status_code=404, detail="job/profile not found")

    result = await HybridApplicator().apply(job, payload={"resume": profile.master_resume})
    job.applied = result.success
    db.add(job)

    attempt = ApplicationAttempt(
        job_id=job.id,
        channel=result.channel,
        status=result.status,
        notes=result.notes,
    )
    db.add(attempt)
    db.commit()
    return {
        "job_id": job.id,
        "status": result.status,
        "channel": result.channel,
        "notes": result.notes,
    }


@router.get("/attempts")
def list_attempts(limit: int = Query(default=200, ge=1, le=1000), db: Session = Depends(get_db)):
    items = db.execute(select(ApplicationAttempt).order_by(desc(ApplicationAttempt.id)).limit(limit)).scalars()
    return [
        {
            "id": x.id,
            "job_id": x.job_id,
            "channel": x.channel,
            "status": x.status,
            "notes": x.notes,
            "created_at": x.created_at,
        }
        for x in items
    ]


@router.get("/dashboard/metrics")
def dashboard_metrics(db: Session = Depends(get_db)):
    m = compute_dashboard_metrics(db)
    return {
        "total_jobs": m.total_jobs,
        "applied_jobs": m.applied_jobs,
        "pending_jobs": m.pending_jobs,
        "attempts_total": m.attempts_total,
        "success_rate": m.success_rate,
    }


@router.get("/run-control")
def get_run_control(db: Session = Depends(get_db)):
    ctrl = db.get(RunControl, 1)
    if not ctrl:
        ctrl = RunControl(id=1, is_running=True, updated_at=datetime.utcnow())
        db.add(ctrl)
        db.commit()
        db.refresh(ctrl)
    return {"is_running": ctrl.is_running, "updated_at": ctrl.updated_at}


@router.patch("/run-control")
def update_run_control(payload: RunControlUpdate, db: Session = Depends(get_db)):
    ctrl = db.get(RunControl, 1)
    if not ctrl:
        ctrl = RunControl(id=1)
    ctrl.is_running = payload.is_running
    ctrl.updated_at = datetime.utcnow()
    db.add(ctrl)
    db.commit()
    return {"is_running": ctrl.is_running}


@router.post("/autopilot/run-once")
async def run_autopilot_once():
    count = await run_cycle()
    return {"applied_this_cycle": count}


@router.post("/bootstrap/demo")
def bootstrap_demo(db: Session = Depends(get_db)):
    existing_profiles = db.execute(select(CandidateProfile.id).limit(1)).first()
    if not existing_profiles:
        db.add(
            CandidateProfile(
                full_name="Demo Candidate",
                email="demo@example.com",
                linkedin_url="https://linkedin.com/in/demo",
                master_resume=(
                    "Python backend engineer with FastAPI, SQL, Docker, cloud, and automation experience."
                ),
            )
        )

    demo_jobs = [
        JobListing(
            source="greenhouse",
            company="Acme Labs",
            title="Backend Engineer",
            location="Remote",
            url="https://jobs.example.com/acme-backend",
            description="Build Python APIs with SQL, cloud, and docker.",
        ),
        JobListing(
            source="ashby",
            company="Orbit Analytics",
            title="Technical Program Manager",
            location="Remote",
            url="https://jobs.example.com/orbit-tpm",
            description="Program management, stakeholder updates, analytics, and process automation.",
        ),
    ]

    for item in demo_jobs:
        exists = db.execute(select(JobListing.id).where(JobListing.url == item.url)).first()
        if not exists:
            db.add(item)

    db.commit()
    return {"ok": True}
