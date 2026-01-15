from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class AgentStatus(str, Enum):
    IDLE="idle"
    RUNNING="running"
    COMPLETED="completed"
    FAILED="failed"

@dataclass
class Task:
    id: str
    description: str
    priority: int=5
    depends_on:list[str]=None
    status: str="pending"

    def __post_init__(self)-> None:
        if self.depends_on is None:
            self.depends_on = []


@dataclass
class Episode:
    task_id: str
    input: str
    output: str
    success: bool
    timestamp: str
    
    def to_json(self) -> str:
        return json.dumps(asdict(self))

@dataclass
class AgentState:
    status: AgentStatus
    current_task: str | None
    completed_tasks: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
        return{
            "status": self.status.value,
            "current_task": self.current_task,
            "completed_tasks": self.completed_tasks,
        }