from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

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
    RunControlUpdate,
)
from app.services.applicator import HybridApplicator
from app.services.composer import DraftComposer
from app.services.llm_router import LLMRouter
from app.services.matcher import score_job
from app.services.question_memory import QuestionMemory
from app.core.config import get_settings

router = APIRouter(prefix="/v1", tags=["job-automation"])


@router.post("/profiles")
def create_profile(payload: CandidateProfileCreate, db: Session = Depends(get_db)):
    profile = CandidateProfile(**payload.model_dump())
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"id": profile.id}


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
