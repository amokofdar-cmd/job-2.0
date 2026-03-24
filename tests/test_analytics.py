from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.entities import ApplicationAttempt, JobListing
from app.services.analytics import compute_dashboard_metrics


def test_dashboard_metrics_calculates_fields():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, future=True)()

    session.add_all(
        [
            JobListing(
                source="test",
                company="A",
                title="Backend Engineer",
                location="Remote",
                url="https://example.com/job/1",
                description="python",
                applied=True,
            ),
            JobListing(
                source="test",
                company="B",
                title="Platform Engineer",
                location="Remote",
                url="https://example.com/job/2",
                description="infra",
                applied=False,
            ),
        ]
    )
    session.commit()
    session.add_all(
        [
            ApplicationAttempt(job_id=1, channel="api", status="submitted", notes="ok"),
            ApplicationAttempt(job_id=2, channel="browser", status="failed", notes="x"),
        ]
    )
    session.commit()

    metrics = compute_dashboard_metrics(session)

    assert metrics.total_jobs == 2
    assert metrics.applied_jobs == 1
    assert metrics.pending_jobs == 1
    assert metrics.attempts_total == 2
    assert metrics.success_rate == 0.5
