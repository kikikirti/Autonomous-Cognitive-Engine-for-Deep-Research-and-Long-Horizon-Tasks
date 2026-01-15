from __future__ import annotations

from dataclasses import dataclass

from ace.core.memory import Memory
from ace.core.planner import Planner
from ace.core.queue import TaskQueue
from ace.core.reasoner import Reasoner
from ace.core.reflector import Reflector
from ace.core.tools import ToolExecutor


@dataclass
class Agent:

    memory: Memory
    planner: Planner
    reasoner: Reasoner
    reflector: Reflector
    tool_executor: ToolExecutor
    queue: TaskQueue

    def __init__(
            self,
            memory: Memory,
            planner: Planner,
            reasoner: Reasoner,
            reflector: Reflector,
            tools: ToolExecutor | None=None,
            tool_executor: ToolExecutor | None=None,
            queue: TaskQueue | None=None,
            task_queue: TaskQueue | None=None,
    )-> None:
        self.memory = memory
        self.planner = planner
        self.reasoner = reasoner
        self.reflector = reflector
        
        self.queue = queue if queue is not None else task_queue
        self.tools= tools if tools is not None else tool_executor

        if self.queue is None:
            self.queue = TaskQueue()
        if self.tools is None:
            raise TypeError("Missing required argument: tools/tool_executor")
    

    def run(self,goal:str) -> None:
        self.memory.short_term["goal"]=goal
