from __future__ import annotations

from statistics import mean
from typing import List

from sqlalchemy.orm import Session

from .debate import DebateManager, DebateSession
from .schemas import EvaluationResponse, EvaluationScores, MessagePayload


class EvaluationService: # derive aqs metrics
    def __init__(self, debate_manager: DebateManager) -> None:
        self.debate_manager = debate_manager

    def evaluateSession(self, db: Session, session_id: str) -> EvaluationResponse: # evaluate persisted session
        session = self.debate_manager.getSession(db, session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        history = session.historyMessages()
        assistant_messages = [msg for msg in history if msg.role == "assistant"]

        clarity = self._scoreClarity(assistant_messages)
        evidence = self._scoreEvidence(assistant_messages)
        logic = self._scoreLogic(assistant_messages)
        rebuttal = self._scoreRebuttal(history)

        opposition_consistency = (self.debate_manager.oppositionRatio(session) * 100)
        hallucination_rate = self.debate_manager.hallucinationRate(session) * 100
        aqs_overall = round(mean([clarity, evidence, logic, rebuttal]), 2)
        label = self._labelScore(aqs_overall, hallucination_rate, opposition_consistency)
        notes = self._notesForLabel(label)

        scores = EvaluationScores(
            clarity=round(clarity, 2),
            evidence=round(evidence, 2),
            logic=round(logic, 2),
            rebuttal=round(rebuttal, 2),
        )
        return EvaluationResponse(
            session_id=session.id,
            aqs_overall=aqs_overall,
            scores=scores,
            hallucination_rate=round(hallucination_rate, 2),
            opposition_consistency=round(opposition_consistency, 2),
            label=label,
            notes=notes,
        )

    def _scoreClarity(self, messages: List[MessagePayload]) -> float: # score clarity
        if not messages:
            return 1.0
        avg_length = mean(len(msg.content.split()) for msg in messages)
        return self._clampValue(2.0 + (avg_length / 60), 1.0, 5.0)

    def _scoreEvidence(self, messages: List[MessagePayload]) -> float: # reward turns that cite sources
        total_citations = sum(len(msg.citations) for msg in messages)
        return self._clampValue(1.5 + (total_citations * 0.8), 1.0, 5.0)

    def _scoreLogic(self, messages: List[MessagePayload]) -> float: # look for logical markers
        coherent = sum(1 for msg in messages if "therefore" in msg.content.lower())
        ratio = coherent / len(messages) if messages else 0
        return self._clampValue(2.2 + ratio * 2.5, 1.0, 5.0)

    def _scoreRebuttal(self, history: List[MessagePayload]) -> float: # count paired exchanges
        pairings = min(
            sum(1 for msg in history if msg.role == "assistant"),
            sum(1 for msg in history if msg.role == "user"),
        )
        return self._clampValue(2.0 + pairings * 0.5, 1.0, 5.0)

    def _labelScore(self, aqs: float, hallucination_rate: float, opposition: float) -> str: # map metrics to labels
        if aqs < 3.0 or hallucination_rate > 25 or opposition < 60:
            return "Poor"
        if 3.0 <= aqs <= 3.5 or 15 < hallucination_rate <= 25 or 60 <= opposition <= 75:
            return "Okay"
        if 3.6 <= aqs <= 4.2 or 5 < hallucination_rate <= 15 or 76 <= opposition <= 90:
            return "Good"
        if aqs > 4.2 and hallucination_rate < 5 and opposition > 90:
            return "Excellent"
        return "Okay"

    def _notesForLabel(self, label: str) -> str: # return coaching language
        mapping = {
            "Poor": "Substantial issues detected — revisit grounding and stance control.",
            "Okay": "Serviceable debate, but evidence and consistency need work.",
            "Good": "Generally strong opposition with minor polish needed.",
            "Excellent": "High-quality debate with confident, grounded opposition.",
        }
        return mapping.get(label, "")

    def _clampValue(self, value: float, lower: float, upper: float) -> float: # restrict heuristic scores
        return max(lower, min(upper, value))
