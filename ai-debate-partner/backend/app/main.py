"""FastAPI entrypoint wiring debate and evaluation endpoints."""

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import getSession, initDb
from .debate import DebateManager
from .evaluation import EvaluationService
from .llm import DebateLLM
from .retrieval import CorpusRetriever
from .schemas import (
    DebateRespondRequest,
    DebateRespondResponse,
    EvaluationRequest,
    EvaluationResponse,
    StartDebateRequest,
    StartDebateResponse,
)

app = FastAPI(title="AI Debate Partner", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = CorpusRetriever()
llm = DebateLLM()
debate_manager = DebateManager(retriever=retriever, llm=llm)
evaluation_service = EvaluationService(debate_manager=debate_manager)


@app.on_event("startup")
def onStartup() -> None:
    initDb()
    retriever.refreshCorpus()


@app.get("/health")
def healthCheck() -> dict[str, str]:
    """Return a simple readiness probe for deployment checks."""
    return {"status": "ok"}


@app.post("/debate/start", response_model=StartDebateResponse)
def debateStart(
    payload: StartDebateRequest,
    db: Session = Depends(getSession),
) -> StartDebateResponse:
    """Open a new debate session and return the first assistant turn."""
    session, reply, citations, hallucinations, opposition_consistent = debate_manager.startSession(
        db,
        topic=payload.topic,
        stance=payload.stance,
    )
    return StartDebateResponse(
        session_id=session.id,
        ai_message=reply,
        citations=citations,
        hallucination_flags=hallucinations,
        opposition_consistent=opposition_consistent,
    )


@app.post("/debate/respond", response_model=DebateRespondResponse)
def debateRespond(
    payload: DebateRespondRequest,
    db: Session = Depends(getSession),
) -> DebateRespondResponse:
    """Record a user rebuttal and stream back the assistant reply."""
    session = debate_manager.getSession(db, payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    reply, citations, hallucinations, opposition_consistent = debate_manager.respond(
        db,
        session=session,
        user_message=payload.user_message,
    )
    return DebateRespondResponse(
        session_id=session.id,
        ai_message=reply,
        citations=citations,
        hallucination_flags=hallucinations,
        opposition_consistent=opposition_consistent,
    )


@app.post("/evaluate", response_model=EvaluationResponse)
def evaluateSession(
    payload: EvaluationRequest,
    db: Session = Depends(getSession),
) -> EvaluationResponse:
    """Compute rubric feedback for the requested session."""
    try:
        return evaluation_service.evaluateSession(db, payload.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
