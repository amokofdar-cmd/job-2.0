"""Seed demo data for quick manual testing.

Run:
  python scripts/seed_demo.py
"""

from app.db.session import SessionLocal
from app.models.entities import CandidateProfile, JobListing


def main():
    with SessionLocal() as db:
        if not db.query(CandidateProfile).count():
            db.add(
                CandidateProfile(
                    full_name="Demo Candidate",
                    email="demo@example.com",
                    linkedin_url="https://linkedin.com/in/demo",
                    master_resume="Python FastAPI SQL backend cloud docker automation",
                    preferences_json='{"remote": true}',
                )
            )

        sample_jobs = [
            JobListing(
                source="greenhouse",
                company="Acme",
                title="Backend Engineer",
                location="Remote",
                url="https://example.com/jobs/backend-1",
                description="Python backend APIs SQL cloud",
            ),
            JobListing(
                source="ashby",
                company="Globex",
                title="Platform Engineer",
                location="Remote",
                url="https://example.com/jobs/platform-1",
                description="Kubernetes infra automation cloud",
            ),
        ]

        for job in sample_jobs:
            exists = db.query(JobListing).filter(JobListing.url == job.url).first()
            if not exists:
                db.add(job)
        db.commit()
    print("Seed complete.")


if __name__ == "__main__":
    main()
