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

    def generateSubtopics(self, topic: str) -> List[str]:
        """Generate 5 relevant subtopics for the given topic."""
        if self.client is not None:
            try:
                prompt = (
                    f"List 5 relevant subtopics for a debate on '{topic}'. "
                    "Return only the subtopics as a numbered list."
                )
                completion = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=1,
                )
                content = self._extractContent(completion)
                if content:
                    # Parse the numbered list
                    lines = [line.strip() for line in content.splitlines() if line.strip()]
                    # Remove numbering (e.g., "1. Subtopic" -> "Subtopic")
                    subtopics = []
                    for line in lines:
                        parts = line.split(".", 1)
                        if len(parts) > 1:
                            subtopics.append(parts[1].strip())
                        else:
                            subtopics.append(line)
                    return subtopics[:5]
            except Exception as exc:
                logger.exception("LLM subtopic generation failed: %s", exc)

        # Fallback if LLM fails or is not configured
        return []

    def generateReply(
        self,
        *,
        topic: str,
        user_stance: str,
        user_message: str,
        context: Iterable[RetrievedContext],
        history: List[LLMMessage],
        context_bundle: Optional[str] = None,
        temperature: float = 1,
    ) -> str:
        """Call the OpenAI API when available."""
        context_items = list(context)
        if context_bundle is None:
            context_bundle, _ = formatContext(context_items)

        if self.client is None:
             return "Failed to get an answer from API: OpenAI client is not initialized."

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
            return "Failed to get an answer from API: Empty response."
        except Exception as exc:
            logger.exception("LLM request failed: %s", exc)
            return f"Failed to get an answer from API: {exc}"

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
                "You are a professional debater tasked with arguing against the user. "
                f"The topic is '{topic}'. The user's stance is: '{user_stance}'. "
                "Your goal is to adopt and maintain the OPPOSITE stance throughout the entire conversation. "
                "Never agree with the user. "
                "Construct compelling counter-arguments using the provided evidence where relevant. "
                "In your opening statement, clearly define the opposing position you will be defending. "
                "Integrate evidence naturally into your argument without explicitly citing filenames or chunk IDs. "
                "Review the conversation history to avoid repeating arguments or evidence. "
                "Directly address the user's latest point. "
                "Open the debate naturally by countering the user's stance."
                "Be concise yet persuasive in your responses. Your response length is somewhat up to your discretion based on what the user prompts you with."
                "While length is somewhat up to your discretion, you MUST keep responses between around 25 and 150 words."
            )
        )
        if context_text:
            instructions.append(
                "Retrieved evidence you can use:\n" + context_text
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
