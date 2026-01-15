from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Planner:
    def decompose(self, goal: str) -> list[str]:
        return [f"Investigate: {goal}", f"Draft plan for: {goal}"]
