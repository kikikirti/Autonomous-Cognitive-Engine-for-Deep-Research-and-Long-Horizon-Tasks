from __future__ import annotations

import hashlib
from dataclasses import dataclass

from ace.core.rag.models import RetrievedChunk


def _fingerprint(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()


@dataclass
class RAGFusion:
    max_chunks: int = 8

    def fuse(self, chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        # Dedupe by content fingerprint
        seen: set[str] = set()
        deduped: list[RetrievedChunk] = []
        for ch in chunks:
            fp = _fingerprint(ch.text)
            if fp in seen:
                continue
            seen.add(fp)
            deduped.append(ch)

        # Rank by confidence (desc)
        deduped.sort(key=lambda c: c.citation.confidence, reverse=True)

        # Keep top-N
        return deduped[: self.max_chunks]
