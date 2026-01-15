from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any
from datetime import datetime
import json

class AgentStatus(str, Enum):
    IDLE="idle"
    RUNNING="running"
    COMPLETED="completed"
    FAILED="failed"

@dataclass
class Task:
    id: str
    description: str
    status: str="pending"


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