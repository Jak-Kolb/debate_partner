"""Lightweight local retrieval over the on-disk corpora."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

DEFAULT_CHUNK_SIZE = 400
DEFAULT_OVERLAP = 40


@dataclass
class RetrievedContext:
    """Chunked document content returned by the retriever."""

    source: str
    content: str


class CorpusRetriever:
    """Lightweight local retriever with a fallback when FAISS is unavailable."""

    def __init__(
        self,
        corpus_dir: Path | None = None,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        overlap: int = DEFAULT_OVERLAP,
    ) -> None:
        base_dir = Path(__file__).resolve().parents[2]
        configured_dir = os.getenv("CORPUS_DIR")
        if corpus_dir is not None:
            self.corpus_dir = Path(corpus_dir)
        elif configured_dir:
            self.corpus_dir = Path(configured_dir)
        else:
            self.corpus_dir = base_dir / "data" / "corpora"
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.documents = self._load_documents()

    def _load_documents(self) -> List[RetrievedContext]:
        """Read and chunk corpus files into retrievable contexts."""
        if not self.corpus_dir.exists():
            return []

        contexts: List[RetrievedContext] = []
        for path in sorted(self.corpus_dir.rglob("*.txt")):
            text = path.read_text(encoding="utf-8")
            for idx, chunk in enumerate(self._chunk_text(text)):
                contexts.append(
                    RetrievedContext(source=f"{path.name}#chunk{idx}", content=chunk)
                )
        return contexts

    def _chunk_text(self, text: str) -> Iterable[str]:
        """Yield overlapping slices of a document for dense retrieval."""
        if len(text) <= self.chunk_size:
            yield text
            return

        step = max(self.chunk_size - self.overlap, 1)
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            if not chunk:
                break
            yield chunk

    def refresh(self) -> None:
        """Reload corpus chunks from disk (used at startup or when docs change)."""
        self.documents = self._load_documents()

    def retrieve(self, query: str, limit: int = 3) -> Sequence[RetrievedContext]:
        """Return the top-N chunks ranked by naive token overlap with the query."""
        if not query or not self.documents:
            return []

        ranked = sorted(
            self.documents,
            key=lambda doc: -self._overlap_score(query.lower(), doc.content.lower()),
        )
        return ranked[:limit]

    def _overlap_score(self, query: str, text: str) -> int:
        """Score overlap using shared tokens as a lightweight similarity proxy."""
        window = set(query.split())
        return sum(1 for token in window if token in text)


def format_context(contexts: Sequence[RetrievedContext]) -> Tuple[str, List[str]]:
    """Aggregate retrieval chunks into a citation bundle for prompting."""
    if not contexts:
        return "", []

    aggregate_lines: List[str] = []
    citations: List[str] = []
    for ctx in contexts:
        citations.append(ctx.source)
        aggregate_lines.append(f"Source: {ctx.source}\n{ctx.content.strip()}")
    return "\n\n".join(aggregate_lines), citations
