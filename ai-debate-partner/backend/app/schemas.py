"""Pydantic schemas describing debate session payloads."""

from typing import List, Optional

from pydantic import BaseModel, Field


class StartDebateRequest(BaseModel):
    """Client request for opening a new debate session."""
    topic: str = Field(..., description="Debate topic or question")
    stance: str = Field(..., description="User's position that the AI should oppose")


class MessagePayload(BaseModel):
    """Normalized message stored in persistent session history."""
    role: str
    content: str
    citations: List[str] = Field(default_factory=list)


class StartDebateResponse(BaseModel):
    """Initial assistant reply and metadata returned after session creation."""
    session_id: str
    ai_message: str
    citations: List[str] = Field(default_factory=list)
    hallucination_flags: List[str] = Field(default_factory=list)
    opposition_consistent: bool


class DebateRespondRequest(BaseModel):
    """User rebuttal payload for an existing debate session."""
    session_id: str
    user_message: str


class DebateRespondResponse(BaseModel):
    """Assistant counter-response enriched with citations and flags."""
    session_id: str
    ai_message: str
    citations: List[str] = Field(default_factory=list)
    hallucination_flags: List[str] = Field(default_factory=list)
    opposition_consistent: bool


class EvaluationRequest(BaseModel):
    """Request to compute rubric feedback for a completed session."""
    session_id: str


class EvaluationScores(BaseModel):
    """Breakdown of the AQS rubric sub-scores."""
    clarity: float
    evidence: float
    logic: float
    rebuttal: float


class EvaluationResponse(BaseModel):
    """Aggregated evaluation metrics surfaced to the frontend."""
    session_id: str
    aqs_overall: float
    scores: EvaluationScores
    hallucination_rate: float
    opposition_consistency: float
    label: str
    notes: Optional[str] = None
