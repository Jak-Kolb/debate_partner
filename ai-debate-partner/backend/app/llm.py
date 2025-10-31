"""LLM abstraction that injects anti-sycophancy and factual guardrails."""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional

openai_spec = importlib.util.find_spec("openai")
if openai_spec:  # pragma: no cover - runtime import when available
    openai_module = importlib.import_module("openai")
    OpenAI = getattr(openai_module, "OpenAI", None)
else:  # pragma: no cover - handled in runtime fallback
    OpenAI = None

OpenAIClient = Any

from .retrieval import RetrievedContext, formatContext

PROMPT_DIR = Path(__file__).parent / "prompts"
DEFAULT_MODEL = "gpt-4o-mini"
logger = logging.getLogger(__name__)


def _loadPrompt(name: str) -> str:
    path = PROMPT_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8").strip()
    return ""


@dataclass
class LLMMessage:
    """Minimal chat-style message used to pass history into the model stub."""

    role: str
    content: str


class DebateLLM:
    """Abstraction layer for OpenAI chat completions with a deterministic fallback."""

    def __init__(self, *, client: Optional[OpenAIClient] = None, model_name: Optional[str] = None) -> None:
        """Load reusable system prompts once per process and configure the LLM client."""
        self.antisycophancy_prompt = _loadPrompt("system_antisycophancy.txt")
        self.guardrails_prompt = _loadPrompt("system_factuality_guardrails.txt")
        self.model_name = model_name or os.getenv("MODEL_NAME") or DEFAULT_MODEL
        self.client: Optional[OpenAIClient]
        self.client = client or self._initClient()

    def _initClient(self) -> Optional[OpenAIClient]:
        """Initialise the OpenAI client when credentials are present."""
        if OpenAI is None:
            logger.warning("openai package not available; using deterministic fallback replies.")
            return None

        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("No LLM API key configured; using deterministic fallback replies.")
            return None

        base_url = os.getenv("API_BASE") or os.getenv("OPENAI_BASE_URL")
        try:
            return OpenAI(api_key=api_key, base_url=base_url)
        except Exception as exc:  # pragma: no cover - defensive against SDK issues
            logger.exception("Failed to initialise OpenAI client: %s", exc)
            return None

    def buildSystemPrompt(self) -> str:
        """Compose guardrail prompts into a single system instruction block."""
        prompts = [self.antisycophancy_prompt, self.guardrails_prompt]
        return "\n\n".join([p for p in prompts if p])

    def generateReply(
        self,
        *,
        topic: str,
        user_stance: str,
        user_message: str,
        context: Iterable[RetrievedContext],
        history: List[LLMMessage],
        context_bundle: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Call the OpenAI API when available and fall back to a deterministic reply."""
        context_items = list(context)
        if context_bundle is None:
            context_bundle, _ = formatContext(context_items)

        if self.client is not None:
            messages = self._buildChatMessages(
                topic=topic,
                user_stance=user_stance,
                user_message=user_message,
                history=history,
                context_text=context_bundle,
            )
            try:
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=temperature,
                )
                content = self._extractContent(completion)
                if content:
                    return content
            except Exception as exc:  # pragma: no cover - defensive against API/runtime failures
                logger.exception("LLM request failed, using fallback reply: %s", exc)

        return self._fallbackReply(
            topic=topic,
            user_stance=user_stance,
            user_message=user_message,
            context=context_items,
        )

    def _buildChatMessages(
        self,
        *,
        topic: str,
        user_stance: str,
        user_message: str,
        history: List[LLMMessage],
        context_text: str,
    ) -> List[dict[str, str]]:
        """Translate persisted history and retrieval context into chat messages."""
        instructions = [self.buildSystemPrompt()]
        instructions.append(
            (
                "You are participating in a structured debate. The user supports the stance "
                f"'{user_stance}' on the topic '{topic}'. Always respond with a cogent counter-argument, "
                "reference evidence when available, and maintain a respectful tone. Cite sources "
                "by their identifier when you rely on them."
            )
        )
        if context_text:
            instructions.append(
                "Retrieved evidence you can cite:\n" + context_text
            )
        else:
            instructions.append(
                "No supporting documents were retrieved. Flag uncertainty when making claims that are not grounded."
            )

        system_message = "\n\n".join(filter(None, instructions)).strip()
        messages: List[dict[str, str]] = [{"role": "system", "content": system_message}]
        for item in history:
            messages.append({"role": item.role, "content": item.content})

        if not history or history[-1].role != "user":
            opener = user_message.strip() or (
                "Please open the debate by presenting a counter-argument to my stance."
            )
            messages.append({"role": "user", "content": opener})

        return messages

    def _extractContent(self, completion: object) -> str:
        """Safely extract assistant content from an OpenAI chat completion response."""
        choices = getattr(completion, "choices", None)
        if not choices:
            return ""
        first_choice = choices[0]
        message = getattr(first_choice, "message", None)
        if not message:
            return ""

        content = getattr(message, "content", None)
        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):  # pragma: no cover - depends on SDK response format
            parts = []
            for part in content:
                text = getattr(part, "text", None)
                if text:
                    parts.append(text)
            return "\n".join(parts).strip()

        return ""

    def _fallbackReply(
        self,
        *,
        topic: str,
        user_stance: str,
        user_message: str,
        context: Iterable[RetrievedContext],
    ) -> str:
        """Deterministic reply used when the OpenAI API is unavailable."""
        contexts = list(context)
        opposition_line = (
            f"You support '{user_stance}' on '{topic}', so I will argue the opposing position."
        )

        evidence_phrase = "Based on the retrieved evidence:" if contexts else (
            "I could not retrieve grounded evidence specific to this topic."
        )
        evidence_lines: List[str] = []
        for ctx in contexts:
            preview = ctx.content.strip().splitlines()[0][:200]
            evidence_lines.append(f"- {preview} ({ctx.source})")

        if user_message:
            rebuttal = (
                "Your recent point — '"
                + user_message[:160]
                + "' — overlooks trade-offs that weaken your stance."
            )
        else:
            rebuttal = "To open, the policy you advocate raises meaningful risks that deserve scrutiny."

        guidance = (
            "Given the thin evidence, treat this critique as provisional while we surface stronger citations."
            if not contexts
            else "These references indicate viable counterpoints that undermine your argument."
        )

        sections = [opposition_line, evidence_phrase]
        if evidence_lines:
            sections.append("\n".join(evidence_lines))
        sections.extend([rebuttal, guidance])
        return "\n\n".join(part for part in sections if part)

    def oppositionConsistent(self, reply: str, user_stance: str) -> bool:
        """Heuristically detect whether the assistant drifted toward the user stance."""
        stance_tokens = set(user_stance.lower().split())
        matches = sum(1 for token in stance_tokens if token in reply.lower())
        return matches < max(1, len(stance_tokens))

    def detectHallucinations(self, reply: str, context: Iterable[RetrievedContext]) -> List[str]:
        """Flag ungrounded replies when no supporting retrieval context is present."""
        if any(context):
            return []
        return ["No supporting documents found; treat claims as ungrounded."]
