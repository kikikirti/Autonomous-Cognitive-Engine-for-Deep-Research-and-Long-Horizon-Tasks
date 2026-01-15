from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Memory:
    short_term: dict[str, Any] = field(default_factory=dict)
    long_term: list[dict[str, Any]] = field(default_factory=list)

    def add_episode(self, event: dict[str, Any]) -> None:
        self.long_term.append(event)
