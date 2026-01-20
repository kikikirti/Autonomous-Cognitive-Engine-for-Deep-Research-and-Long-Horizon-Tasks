from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolRequest:
    name: str
    input: dict[str, Any]=field(default_factory=dict)
    trace_id: str | None=None


@dataclass
class ToolError:
    code: str
    message: str
    details: dict[str, Any]=field(default_factory=dict)


@dataclass
class ToolResponse:
    ok: bool
    name: str
    output: dict[str, Any]=field(default_factory=dict)
    error: ToolError | None=None
    attempts: int=1
    duration_ms: int | None=None