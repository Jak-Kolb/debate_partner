from __future__ import annotations

import json
from datetime import datetime
from typing import List, Sequence, Tuple
from uuid import uuid4

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Session

from .db import Base
from .llm import DebateLLM, LLMMessage
from .retrieval import CorpusRetriever, RetrievedContext, formatContext
from .schemas import MessagePayload


class DebateSession(Base): # sql model for debate metadata
    __tablename__ = "debate_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    topic = Column(String, nullable=False)
    stance = Column(String, nullable=False)
    history = Column(Text, default="[]", nullable=False)
    assistant_turns = Column(Integer, default=0, nullable=False)
    hallucination_events = Column(Integer, default=0, nullable=False)
    opposition_drift_turns = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def historyMessages(self) -> List[MessagePayload]: # return stored turns
        data = json.loads(self.history or "[]")
        return [MessagePayload(**item) for item in data]

    def appendMessage(self, message: MessagePayload) -> None: # persist new message
        messages = [msg.model_dump() for msg in self.historyMessages()]
        messages.append(message.model_dump())
        self.history = json.dumps(messages)


class DebateManager: # facade for session storage and model responses
    def __init__(self, retriever: CorpusRetriever, llm: DebateLLM) -> None:
        self.retriever = retriever
        self.llm = llm

    def startSession(self, db: Session, *, topic: str, stance: str) -> Tuple[DebateSession, str, List[str], List[str], bool]: # create session and generate opening
        session = DebateSession(topic=topic, stance=stance)
        db.add(session)
        db.flush()

        reply, citations, hallucinations, opposition_consistent = self._generateReply(
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
    ) -> Tuple[str, List[str], List[str], bool]: # persist user rebuttal and return counter-argument
        session.appendMessage(
            MessagePayload(role="user", content=user_message, citations=[])
        )
        reply, citations, hallucinations, opposition_consistent = self._generateReply(
            session=session,
            db=db,
            user_message=user_message,
        )
        return reply, citations, hallucinations, opposition_consistent

    def _generateReply(
        self,
        *,
        session: DebateSession,
        db: Session,
        user_message: str,
    ) -> Tuple[str, List[str], List[str], bool]: # build assistant message and update metrics
        history_payloads = session.historyMessages()
        history = [
            LLMMessage(role=msg.role, content=msg.content)
            for msg in history_payloads
        ]
        contexts = self.retriever.retrieveContexts(
            query=f"{session.topic} {user_message}"
        )
        context_bundle, citations = formatContext(contexts)
        reply = self.llm.generateReply(
            topic=session.topic,
            user_stance=session.stance,
            user_message=user_message,
            context=contexts,
            history=history,
            context_bundle=context_bundle,
        )
        hallucinations = self.llm.detectHallucinations(reply, contexts)
        opposition_consistent = self.llm.oppositionConsistent(reply, session.stance)

        payload = MessagePayload(
            role="assistant",
            content=reply,
            citations=citations,
        )
        session.appendMessage(payload)
        session.assistant_turns += 1
        if not opposition_consistent:
            session.opposition_drift_turns += 1
        if hallucinations:
            session.hallucination_events += 1

        db.add(session)
        db.flush()
        return reply, citations, hallucinations, opposition_consistent

    def getSession(self, db: Session, session_id: str) -> DebateSession | None: # fetch session by id
        return db.query(DebateSession).filter(DebateSession.id == session_id).one_or_none()

    def oppositionRatio(self, session: DebateSession) -> float: # return fraction of turns maintaining opposition
        if session.assistant_turns == 0:
            return 1.0
        return 1 - (session.opposition_drift_turns / session.assistant_turns)

    def hallucinationRate(self, session: DebateSession) -> float: # compute percentage of turns flagged
        if session.assistant_turns == 0:
            return 0.0
        return session.hallucination_events / session.assistant_turns

