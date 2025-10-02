from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from .retrieval import RetrievedContext

PROMPT_DIR = Path(__file__).parent / "prompts"


def _load_prompt(name: str) -> str:
    path = PROMPT_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


@dataclass
class LLMMessage:
    role: str
    content: str


class DebateLLM:
    """Abstraction layer for future LLM providers with deterministic stubs."""

    def __init__(self) -> None:
        self.antisycophancy_prompt = _load_prompt("system_antisycophancy.txt")
        self.guardrails_prompt = _load_prompt("system_factuality_guardrails.txt")

    def build_system_prompt(self) -> str:
        prompts = [self.antisycophancy_prompt, self.guardrails_prompt]
        return "\n\n".join([p for p in prompts if p])

    def generate_reply(
        self,
        *,
        topic: str,
        user_stance: str,
        user_message: str,
        context: Iterable[RetrievedContext],
        history: List[LLMMessage],
    ) -> str:
        basis = self._context_summary(context)
        opposition_line = (
            f"I take the opposing view to your stance '{user_stance}' on '{topic}'."
        )
        evidence_line = basis or "I lack direct evidence in the corpus, so I will flag uncertainty."
        rebuttal_line = (
            f"Regarding your latest point: {user_message[:200]}... I challenge the assumptions and present alternatives."
            if user_message
            else "I will open the debate by presenting a counter-position."
        )
        uncertainty = "Given limited corroboration, consider this a tentative claim." if not basis else ""
        message_parts = [self.build_system_prompt(), opposition_line, evidence_line, rebuttal_line, uncertainty]
        return "\n\n".join(part for part in message_parts if part)

    def _context_summary(self, context: Iterable[RetrievedContext]) -> str:
        items = list(context)
        if not items:
            return ""
        summary_parts = ["Grounded references:"]
        for ctx in items:
            preview = ctx.content.strip().splitlines()[0][:160]
            summary_parts.append(f"- ({ctx.source}) {preview}")
        return "\n".join(summary_parts)

    def opposition_consistent(self, reply: str, user_stance: str) -> bool:
        stance_tokens = set(user_stance.lower().split())
        matches = sum(1 for token in stance_tokens if token in reply.lower())
        return matches < max(1, len(stance_tokens))

    def detect_hallucinations(self, reply: str, context: Iterable[RetrievedContext]) -> List[str]:
        if any(context):
            return []
        return ["No supporting documents found; treat claims as ungrounded."]
