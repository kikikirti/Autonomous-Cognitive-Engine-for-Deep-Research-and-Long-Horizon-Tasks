from __future__ import annotations

from dataclasses import dataclass, field

from ace.core.tools.base import Tool


@dataclass
class ToolRegistry:
    _tools:dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool with name {tool.name} already registered")
        self._tools[tool.name] = tool
    
    def get(self, name: str) -> Tool:
        if name not in self._tools:
            raise ValueError(f"Tool with name {name} not registered")
        return self._tools[name]
    def list_tools(self) -> list[str]:
        return sorted(self._tools.keys())