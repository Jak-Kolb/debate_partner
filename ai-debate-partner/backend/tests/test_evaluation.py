import json

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.debate import DebateManager, DebateSession
from app.evaluation import EvaluationService
from app.llm import DebateLLM
from app.schemas import MessagePayload


class DummyRetriever:
    def retrieve(self, query: str, limit: int = 3):  # pragma: no cover - not used in test
        return []


def create_session(db: Session) -> DebateSession:
    session = DebateSession(topic="Climate Policy", stance="Support carbon tax")
    payloads = [
        MessagePayload(
            role="assistant",
            content=(
                "Therefore, considering multiple economic studies, the opposite stance "
                "risks ignoring revenue recycling benefits."
            ),
            citations=["doc1#chunk0"],
        ),
        MessagePayload(role="user", content="I think carbon taxes hurt consumers.", citations=[]),
        MessagePayload(
            role="assistant",
            content=(
                "Therefore the opposition must recognise that targeted rebates counter cost burdens."
            ),
            citations=["doc2#chunk1"],
        ),
    ]
    session.history = json.dumps([msg.dict() for msg in payloads])
    session.assistant_turns = 2
    session.hallucination_events = 0
    session.opposition_drift_turns = 0
    db.add(session)
    db.commit()
    return session


def test_evaluation_scoring_ranges() -> None:
    engine = create_engine("sqlite:///:memory:")
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)

    with TestingSession() as db:
        session = create_session(db)
        manager = DebateManager(retriever=DummyRetriever(), llm=DebateLLM())
        service = EvaluationService(manager)

        result = service.evaluate_session(db, session.id)

    assert 1.0 <= result.aqs_overall <= 5.0
    assert result.label in {"Poor", "Okay", "Good", "Excellent"}
    assert result.hallucination_rate == 0.0
    assert result.opposition_consistency >= 90.0
