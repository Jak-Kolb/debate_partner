from typing import List, Optional

from pydantic import BaseModel, Field


class StartDebateRequest(BaseModel): # client request for new session
    topic: str = Field(..., description="Debate topic or question")
    stance: str = Field(..., description="User's position that the AI should oppose")


class MessagePayload(BaseModel): # normalized message in history
    role: str
    content: str
    citations: List[str] = Field(default_factory=list)


class StartDebateResponse(BaseModel): # initial assistant reply
    session_id: str
    ai_message: str
    citations: List[str] = Field(default_factory=list)
    hallucination_flags: List[str] = Field(default_factory=list)
    opposition_consistent: bool


class SubtopicRequest(BaseModel): # request for subtopics
    topic: str


class SubtopicResponse(BaseModel): # list of subtopics
    subtopics: List[str]


class UploadRequest(BaseModel): # request to upload text
    content: str


class UploadResponse(BaseModel): # confirmation of upload
    message: str
    filename: str


class DebateRespondRequest(BaseModel): # user rebuttal payload
    session_id: str
    user_message: str


class DebateRespondResponse(BaseModel): # assistant counter-response
    session_id: str
    ai_message: str
    citations: List[str] = Field(default_factory=list)
    hallucination_flags: List[str] = Field(default_factory=list)
    opposition_consistent: bool


class EvaluationRequest(BaseModel): # request for rubric feedback
    session_id: str


class EvaluationScores(BaseModel): # breakdown of aqs scores
    clarity: float
    evidence: float
    logic: float
    rebuttal: float


class EvaluationResponse(BaseModel): # aggregated evaluation metrics
    session_id: str
    aqs_overall: float
    scores: EvaluationScores
    hallucination_rate: float
    opposition_consistency: float
    label: str
    notes: Optional[str] = None
