from __future__ import annotations

import json
from datetime import datetime
from typing import List, Sequence, Tuple
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Session

from .db import Base
from .llm import DebateLLM, LLMMessage
from .retrieval import CorpusRetriever, RetrievedContext, format_context
from .schemas import MessagePayload


class DebateSession(Base):
    __tablename__ = "debate_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    topic = Column(String, nullable=False)
    stance = Column(String, nullable=False)
    history = Column(Text, default="[]", nullable=False)
    assistant_turns = Column(Integer, default=0, nullable=False)
    hallucination_events = Column(Integer, default=0, nullable=False)
    opposition_drift_turns = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def history_messages(self) -> List[MessagePayload]:
        data = json.loads(self.history or "[]")
        return [MessagePayload(**item) for item in data]

    def append_message(self, message: MessagePayload) -> None:
        messages = [msg.dict() for msg in self.history_messages()]
        messages.append(message.dict())
        self.history = json.dumps(messages)


class DebateManager:
    def __init__(self, retriever: CorpusRetriever, llm: DebateLLM) -> None:
        self.retriever = retriever
        self.llm = llm

    def start_session(self, db: Session, *, topic: str, stance: str) -> Tuple[DebateSession, str, List[str], List[str], bool]:
        session = DebateSession(topic=topic, stance=stance)
        db.add(session)
        db.flush()

        reply, citations, hallucinations, opposition_consistent = self._generate_reply(
            session=session,
            db=db,
            user_message="",
        )
        return session, reply, citations, hallucinations, opposition_consistent

    def respond(
        self,
        db: Session,
        *,
        session: DebateSession,
        user_message: str,
    ) -> Tuple[str, List[str], List[str], bool]:
        session.append_message(
            MessagePayload(role="user", content=user_message, citations=[])
        )
        reply, citations, hallucinations, opposition_consistent = self._generate_reply(
            session=session,
            db=db,
            user_message=user_message,
        )
        return reply, citations, hallucinations, opposition_consistent

    def _generate_reply(
        self,
        *,
        session: DebateSession,
        db: Session,
        user_message: str,
    ) -> Tuple[str, List[str], List[str], bool]:
        history_payloads = session.history_messages()
        history = [
            LLMMessage(role=msg.role, content=msg.content)
            for msg in history_payloads
        ]
        contexts = self.retriever.retrieve(
            query=user_message or f"{session.topic} {session.stance}"
        )
        _, citations = format_context(contexts)
        reply = self.llm.generate_reply(
            topic=session.topic,
            user_stance=session.stance,
            user_message=user_message,
            context=contexts,
            history=history,
        )
        hallucinations = self.llm.detect_hallucinations(reply, contexts)
        opposition_consistent = self.llm.opposition_consistent(reply, session.stance)

        payload = MessagePayload(
            role="assistant",
            content=reply,
            citations=citations,
        )
        session.append_message(payload)
        session.assistant_turns += 1
        if not opposition_consistent:
            session.opposition_drift_turns += 1
        if hallucinations:
            session.hallucination_events += 1

        db.add(session)
        db.flush()
        return reply, citations, hallucinations, opposition_consistent

    def get_session(self, db: Session, session_id: str) -> DebateSession | None:
        return db.query(DebateSession).filter(DebateSession.id == session_id).one_or_none()

    def opposition_ratio(self, session: DebateSession) -> float:
        if session.assistant_turns == 0:
            return 1.0
        return 1 - (session.opposition_drift_turns / session.assistant_turns)

    def hallucination_rate(self, session: DebateSession) -> float:
        if session.assistant_turns == 0:
            return 0.0
        return session.hallucination_events / session.assistant_turns

    def history_as_messages(self, session: DebateSession) -> Sequence[MessagePayload]:
        return session.history_messages()
