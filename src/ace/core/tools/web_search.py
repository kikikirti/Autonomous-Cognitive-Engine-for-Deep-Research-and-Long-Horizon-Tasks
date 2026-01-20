from __future__ import annotations

import time

from ace.core.tool_schemas import ToolError, ToolRequest, ToolResponse


class WebSearchTool:
    name="web_search"

    def run(self, request: ToolRequest) -> ToolResponse:
        start=time.time()
        query=str(request.input.get("query","")).strip()
        if not query:
            return ToolResponse(
                ok= False,
                name=self.name,
                error=ToolError(code="INVALID_INPUT",message="Missing 'query'"),
                attempts=1,
                duration_ms=int((time.time()-start)*1000),
            )
        results=[
            {
                "title":"Stub result: Agent memory overview",
                "snippet": f"Stubbed web_search result for query: '{query}'.",
                "url": "https://example.com/stub",
            }

        ]
        return ToolResponse(
            ok=True,
            name=self.name,
            output={"query":query,"results":results},
            attempts=1,
            duration_ms=int((time.time()-start)*1000),
        )