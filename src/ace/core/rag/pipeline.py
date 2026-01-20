from __future__ import annotations

from dataclasses import dataclass

from ace.core.rag.fusion import RAGFusion
from ace.core.rag.models import RetrievedChunk


@dataclass
class RAGResult:
    answer: str
    fused: list[RetrievedChunk]


class RAGPipeline:
    def __init__(self, 
                 web_retriever, 
                 internal_retriever, 
                 fusion: RAGFusion | None = None
                 ) -> None:
        self.web = web_retriever
        self.internal = internal_retriever
        self.fusion = fusion or RAGFusion()

    def run(self, query: str, limit: int = 5) -> RAGResult:
        web_chunks = self.web.retrieve(query=query, limit=limit)
        internal_chunks = self.internal.retrieve(query=query, limit=limit)

        fused = self.fusion.fuse(web_chunks + internal_chunks)
        answer = self._synthesize(query, fused)
        return RAGResult(answer=answer, fused=fused)

    def _synthesize(self, query: str, fused: list[RetrievedChunk]) -> str:
        if not fused:
            return f"No evidence found for: {query}"

        lines: list[str] = []
        lines.append(f"Query: {query}")
        lines.append("")
        lines.append("Evidence-based notes:")
        lines.append("")

        for i, ch in enumerate(fused, start=1):
            snippet = ch.text.replace("\n", " ").strip()
            lines.append(f"- {snippet} [{i}]")

        lines.append("")
        lines.append("Citations:")
        for i, ch in enumerate(fused, start=1):
            c = ch.citation
            lines.append(
                f"[{i}] {c.source} | {c.source_id} | {c.timestamp} | "
                f" conf={c.confidence:.2f}"
                )

        return "\n".join(lines)
