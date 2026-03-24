from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.entities import QuestionAnswer
from app.services.question_memory import QuestionMemory


def test_question_memory_upsert():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine, future=True)()

    qm = QuestionMemory(session)
    first = qm.save("Are you authorized to work in the US?", "Yes", True)
    second = qm.save("Are you authorized to work in the US?", "Yes", True)

    assert first.id == second.id
    assert session.query(QuestionAnswer).count() == 1
