from typing import List, Optional

from pydantic import BaseModel, Field


class StartDebateRequest(BaseModel):
    topic: str = Field(..., description="Debate topic or question")
    stance: str = Field(..., description="User's position that the AI should oppose")


class MessagePayload(BaseModel):
    role: str
    content: str
    citations: List[str] = Field(default_factory=list)


class StartDebateResponse(BaseModel):
    session_id: str
    ai_message: str
    citations: List[str] = Field(default_factory=list)
    hallucination_flags: List[str] = Field(default_factory=list)
    opposition_consistent: bool


class DebateRespondRequest(BaseModel):
    session_id: str
    user_message: str


class DebateRespondResponse(BaseModel):
    session_id: str
    ai_message: str
    citations: List[str] = Field(default_factory=list)
    hallucination_flags: List[str] = Field(default_factory=list)
    opposition_consistent: bool


class EvaluationRequest(BaseModel):
    session_id: str


class EvaluationScores(BaseModel):
    clarity: float
    evidence: float
    logic: float
    rebuttal: float


class EvaluationResponse(BaseModel):
    session_id: str
    aqs_overall: float
    scores: EvaluationScores
    hallucination_rate: float
    opposition_consistency: float
    label: str
    notes: Optional[str] = None
