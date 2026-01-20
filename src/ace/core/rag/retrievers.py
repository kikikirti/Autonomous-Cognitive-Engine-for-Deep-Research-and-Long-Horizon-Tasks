from __future__ import annotations

from datetime import datetime, timezone

from ace.core.rag.models import Citation, RetrievedChunk
from ace.core.tool_schemas import ToolRequest


class WebRetriever:
    def __init__(self, tool_executor) -> None:
        self.tools = tool_executor

    def retrieve(self, query: str, limit: int = 5) -> list[RetrievedChunk]:
        req = ToolRequest(
            name="web_search",
            input={"query": query, "limit": limit},
            trace_id=f"web:{query[:24]}",
        )
        resp = self.tools.execute(req)
        if not resp.ok:
            return []

        ts = datetime.now(timezone.utc).isoformat()
        results = resp.output.get("results", [])
        chunks: list[RetrievedChunk] = []

        for r in results[:limit]:
            url = str(r.get("url", ""))
            title = str(r.get("title", "")).strip()
            snippet = str(r.get("snippet", "")).strip()

            text = "\n".join([p for p in [title, snippet] if p])
            if not text:
                continue

            cit = Citation(
                source="web",
                source_id=url or "unknown",
                timestamp=ts,
                snippet=snippet[:240],
                confidence=0.60,
            )
            chunks.append(RetrievedChunk(text=text, citation=cit))

        return chunks


class InternalRetriever:
    def __init__(self, memory_system) -> None:
        self.memory = memory_system

    def retrieve(self, query: str, limit: int = 5) -> list[RetrievedChunk]:
        ts = datetime.now(timezone.utc).isoformat()
        recs = self.memory.recall_long_term(query=query, limit=limit)
        chunks: list[RetrievedChunk] = []

        for r in recs:
            rid = str(r.get("id", ""))
            text = str(r.get("text", "")).strip()
            if not text:
                continue

            cit = Citation(
                source="internal",
                source_id=rid,
                timestamp=ts,
                snippet=text[:240],
                confidence=0.70,
            )
            chunks.append(RetrievedChunk(text=text, citation=cit))

        return chunks
