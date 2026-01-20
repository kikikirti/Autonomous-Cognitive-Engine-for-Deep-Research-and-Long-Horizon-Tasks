from __future__ import annotations

from typing import Protocol

from ace.core.tool_schemas import ToolRequest, ToolResponse


class Tool(Protocol):
    name: str
    def run(self, request: ToolRequest) -> ToolResponse: ...