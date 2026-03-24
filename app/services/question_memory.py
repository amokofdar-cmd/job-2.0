from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import QuestionAnswer
from app.services.utils import question_key


class QuestionMemory:
    def __init__(self, db: Session):
        self.db = db

    def lookup(self, question_text: str) -> QuestionAnswer | None:
        qk = question_key(question_text)
        stmt = select(QuestionAnswer).where(QuestionAnswer.question_key == qk)
        return self.db.execute(stmt).scalar_one_or_none()

    def save(self, question_text: str, answer_text: str, approved: bool = True) -> QuestionAnswer:
        qk = question_key(question_text)
        existing = self.lookup(question_text)
        if existing:
            existing.answer_text = answer_text
            existing.approved = approved
            self.db.add(existing)
            self.db.commit()
            self.db.refresh(existing)
            return existing

        item = QuestionAnswer(
            question_key=qk,
            question_text=question_text,
            answer_text=answer_text,
            approved=approved,
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item
