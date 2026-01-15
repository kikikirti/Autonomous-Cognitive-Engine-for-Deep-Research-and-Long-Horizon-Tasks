from __future__ import annotations

from dataclasses import dataclass

from ace.core.models import Task


class PlannerInterface:
    def decompose(self, goal: str) -> list[Task]:
        raise NotImplementedError


@dataclass
class RuleBasedPlanner(PlannerInterface):

    def decompose(self, goal: str) -> list[Task]:
        t1 = Task(id="t1", description=f"Clarify scope and assumptions for: {goal}", priority=1)
        t2 = Task(
            id="t2",
            description=f"Collect key points / sources for: {goal}",
            priority=2,
            depends_on=["t1"],
        )
        t3 = Task(
            id="t3",
            description=f"Draft structured output for: {goal}",
            priority=3,
            depends_on=["t2"],
        )
        t4 = Task(
            id="t4",
            description=f"Review and refine the draft for: {goal}",
            priority=4,
            depends_on=["t3"],
        )
        return [t1, t2, t3, t4]
Planner=RuleBasedPlanner