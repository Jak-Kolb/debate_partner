import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

DEFAULT_CHUNK_SIZE = 400
DEFAULT_OVERLAP = 40

STOP_WORDS = {
    "the", "is", "at", "which", "on", "and", "a", "an", "in", "to", "of",
    "for", "it", "that", "this", "with", "as", "by", "from", "or", "but",
    "not", "be", "are", "was", "were", "so", "if", "what", "where", "when",
    "why", "how", "i", "you", "he", "she", "they", "we", "my", "your",
    "think", "believe", "opinion", "better", "worse", "vs", "versus"
}


@dataclass
class RetrievedContext: # chunked document content
    source: str
    content: str


class CorpusRetriever: # lightweight local retriever
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
        self.documents = self._loadDocuments()

    def _loadDocuments(self) -> List[RetrievedContext]: # read and chunk corpus files
        if not self.corpus_dir.exists():
            return []

        contexts: List[RetrievedContext] = []
        for path in sorted(self.corpus_dir.rglob("*.txt")):
            text = path.read_text(encoding="utf-8")
            for idx, chunk in enumerate(self._chunkText(text)):
                contexts.append(
                    RetrievedContext(source=f"{path.name}#chunk{idx}", content=chunk)
                )
        return contexts

    def _chunkText(self, text: str) -> Iterable[str]: # yield overlapping slices
        if len(text) <= self.chunk_size:
            yield text
            return

        step = max(self.chunk_size - self.overlap, 1)
        for start in range(0, len(text), step):
            chunk = text[start : start + self.chunk_size]
            if not chunk:
                break
            yield chunk

    def saveDocument(self, content: str) -> str: # save new document
        if not self.corpus_dir.exists():
            self.corpus_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"upload_{uuid.uuid4().hex}.txt"
        file_path = self.corpus_dir / filename
        file_path.write_text(content, encoding="utf-8")
        
        # refresh in-memory documents
        self.refreshCorpus()
        return filename

    def refreshCorpus(self) -> None: # reload corpus chunks
        self.documents = self._loadDocuments()

    def clearCorpus(self) -> None: # delete all files in corpus
        if self.corpus_dir.exists():
            for path in self.corpus_dir.glob("*.txt"):
                try:
                    path.unlink()
                except OSError:
                    pass  # best effort deletion
        self.documents = []

    def retrieveContexts(self, query: str, limit: int = 3) -> Sequence[RetrievedContext]: # return top-n chunks
        if not query or not self.documents:
            return []

        ranked = sorted(
            self.documents,
            key=lambda doc: -self._overlapScore(query.lower(), doc.content.lower()),
        )
        return ranked[:limit]

    def _overlapScore(self, query: str, text: str) -> int: # score overlap
        window = set(word for word in query.split() if word not in STOP_WORDS)
        if not window:
            return 0
        return sum(1 for token in window if token in text)


def formatContext(contexts: Sequence[RetrievedContext]) -> Tuple[str, List[str]]: # aggregate retrieval chunks
    if not contexts:
        return "", []

    aggregate_lines: List[str] = []
    citations: List[str] = []
    for ctx in contexts:
        citations.append(ctx.source)
        aggregate_lines.append(f"Source: {ctx.source}\n{ctx.content.strip()}")
    return "\n\n".join(aggregate_lines), citations
