import asyncio
from sqlalchemy import select

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.entities import ApplicationAttempt, CandidateProfile, JobListing, RunControl
from app.services.applicator import HybridApplicator
from app.services.matcher import score_job


async def run_cycle() -> int:
    applied_count = 0
    with SessionLocal() as db:
        control = db.get(RunControl, 1)
        if control and not control.is_running:
            return 0

        profile = db.execute(select(CandidateProfile).limit(1)).scalar_one_or_none()
        if not profile:
            return 0

        settings = get_settings()
        pending_jobs = db.execute(
            select(JobListing).where(JobListing.applied.is_(False)).limit(settings.autopilot_max_per_cycle)
        ).scalars()

        applicator = HybridApplicator()
        for job in pending_jobs:
            match = score_job(profile.master_resume, job.description)
            job.score = match.score
            job.tier = match.tier

            if job.tier == "C":
                continue

            result = await applicator.apply(job, payload={"resume": profile.master_resume})
            if result.success:
                job.applied = True
                applied_count += 1

            db.add(
                ApplicationAttempt(
                    job_id=job.id,
                    channel=result.channel,
                    status=result.status,
                    notes=result.notes,
                    metadata_json=f'{{"tier":"{job.tier}","score":{job.score}}}',
                )
            )
            db.add(job)

        db.commit()
    return applied_count


async def loop_forever():
    settings = get_settings()
    while True:
        count = await run_cycle()
        print(f"[autopilot] applied this cycle: {count}")
        await asyncio.sleep(settings.autopilot_interval_seconds)


if __name__ == "__main__":
    asyncio.run(loop_forever())
