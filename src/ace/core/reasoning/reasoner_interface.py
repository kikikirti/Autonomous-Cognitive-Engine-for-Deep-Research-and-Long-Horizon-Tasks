from __future__ import annotations

from typing import Protocol

from ace.core.reasoning.action_schema import ActionPlan


class ReasonerInterface(Protocol):
    def plan(self, task_text: str) -> ActionPlan: ...
