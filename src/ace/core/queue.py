from __future__ import annotations

import heapq
from dataclasses import dataclass, field

from ace.core.models import Task


@dataclass
class TaskQueue:
    _heap: list[tuple[int, int, Task]] = field(default_factory=list)
    _counter: int = 0  

    def push_many(self, tasks: list[Task]) -> None:
        for t in tasks:
            self.push(t)

    def push(self, task: Task) -> None:
        
        heapq.heappush(self._heap, (task.priority, self._counter, task))
        self._counter += 1

    def pop_ready(self, completed_task_ids: set[str]) -> Task | None:
        
        if not self._heap:
            return None

        temp: list[tuple[int, int, Task]] = []
        chosen: Task | None = None

        while self._heap:
            pr, c, task = heapq.heappop(self._heap)
            if all(dep in completed_task_ids for dep in task.depends_on):
                chosen = task
                break
            temp.append((pr, c, task))

        
        for item in temp:
            heapq.heappush(self._heap, item)

        return chosen

    def __len__(self) -> int:
        return len(self._heap)
