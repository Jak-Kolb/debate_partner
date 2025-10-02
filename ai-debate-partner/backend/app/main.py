from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .db import get_session, init_db
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
def on_startup() -> None:
    init_db()
    retriever.refresh()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/debate/start", response_model=StartDebateResponse)
def debate_start(
    payload: StartDebateRequest,
    db: Session = Depends(get_session),
) -> StartDebateResponse:
    session, reply, citations, hallucinations, opposition_consistent = debate_manager.start_session(
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
def debate_respond(
    payload: DebateRespondRequest,
    db: Session = Depends(get_session),
) -> DebateRespondResponse:
    session = debate_manager.get_session(db, payload.session_id)
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
def evaluate(
    payload: EvaluationRequest,
    db: Session = Depends(get_session),
) -> EvaluationResponse:
    try:
        return evaluation_service.evaluate_session(db, payload.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
