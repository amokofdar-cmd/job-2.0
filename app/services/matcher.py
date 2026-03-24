from dataclasses import dataclass
from app.services.utils import normalize_text


KEYWORDS_A = {"python", "backend", "api", "sql", "cloud", "fastapi", "docker"}
KEYWORDS_B = {"project", "stakeholder", "operations", "analytics", "automation"}


@dataclass
class MatchResult:
    score: float
    tier: str


def score_job(resume_text: str, description: str) -> MatchResult:
    resume = set(normalize_text(resume_text).split(" "))
    desc = set(normalize_text(description).split(" "))
    overlap = len(resume.intersection(desc))
    denom = max(len(desc), 1)
    base_score = overlap / denom

    bonus_a = len(desc.intersection(KEYWORDS_A)) * 0.015
    bonus_b = len(desc.intersection(KEYWORDS_B)) * 0.008
    score = min(base_score + bonus_a + bonus_b, 1.0)

    if score >= 0.16:
        tier = "A"
    elif score >= 0.08:
        tier = "B"
    else:
        tier = "C"
    return MatchResult(score=round(score, 4), tier=tier)
