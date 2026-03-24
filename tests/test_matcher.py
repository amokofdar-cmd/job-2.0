from app.services.matcher import score_job


def test_score_job_returns_tier_and_score_bounds():
    resume = "Python FastAPI SQL cloud automation"
    desc = "Backend engineer with Python SQL APIs and cloud deployment"
    result = score_job(resume, desc)

    assert 0 <= result.score <= 1
    assert result.tier in {"A", "B", "C"}


def test_score_job_higher_overlap_scores_better():
    resume = "python backend api sql"
    hi = score_job(resume, "python backend api sql engineer")
    lo = score_job(resume, "sales marketing field outreach")

    assert hi.score > lo.score
