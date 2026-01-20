from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ReflectionResult:
    score: float  # 0.0 - 1.0
    issues: list[str] = field(default_factory=list)
    improvements: list[str] = field(default_factory=list)
    redo: bool = False
    suggested_query: str | None = None
    escalate_to_human: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "issues": self.issues,
            "improvements": self.improvements,
            "redo": self.redo,
            "suggested_query": self.suggested_query,
            "escalate_to_human": self.escalate_to_human,
        }
