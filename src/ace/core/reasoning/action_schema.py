from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

ActionType = Literal["THINK", "TOOL_CALL", "ASK_HUMAN", "STOP"]


@dataclass
class ToolCall:
    name: str
    input: dict[str, Any] = field(default_factory=dict)


@dataclass
class ActionPlan:
    action: ActionType
    rationale: str
    tool_call: ToolCall | None = None
    ask: str | None = None
    stop_reason: str | None = None
    requires_approval: bool = False
