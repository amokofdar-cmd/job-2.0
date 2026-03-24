from dataclasses import dataclass
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.entities import ApplicationAttempt, JobListing


@dataclass
class DashboardMetrics:
    total_jobs: int
    applied_jobs: int
    pending_jobs: int
    attempts_total: int
    success_rate: float


def compute_dashboard_metrics(db: Session) -> DashboardMetrics:
    total_jobs = db.execute(select(func.count(JobListing.id))).scalar_one()
    applied_jobs = db.execute(select(func.count(JobListing.id)).where(JobListing.applied.is_(True))).scalar_one()
    attempts_total = db.execute(select(func.count(ApplicationAttempt.id))).scalar_one()
    successful_attempts = db.execute(
        select(func.count(ApplicationAttempt.id)).where(ApplicationAttempt.status == "submitted")
    ).scalar_one()

    pending_jobs = max(total_jobs - applied_jobs, 0)
    success_rate = round((successful_attempts / attempts_total) if attempts_total else 0.0, 4)

    return DashboardMetrics(
        total_jobs=total_jobs,
        applied_jobs=applied_jobs,
        pending_jobs=pending_jobs,
        attempts_total=attempts_total,
        success_rate=success_rate,
    )
