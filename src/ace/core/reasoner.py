from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Reasoner:
    def choose_next(self, task: str | None) -> str | None:
        return task
