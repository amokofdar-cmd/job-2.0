import hashlib
import re


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def question_key(question: str) -> str:
    return hashlib.sha256(normalize_text(question).encode("utf-8")).hexdigest()[:20]
