from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ace.core.agent import Agent
from ace.core.models import AgentState, AgentStatus, Episode, Task
from ace.core.queue import TaskQueue
from ace.core.stop import StopConfig, StopTracker

AUDIT_DIR = Path("audit")
AUDIT_DIR.mkdir(exist_ok=True)


class AgentStateMachine:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.state = AgentState(status=AgentStatus.IDLE, current_task=None, completed_tasks=0)

    def run_once(self, task: Task) -> bool:
        self.state.status = AgentStatus.RUNNING
        self.state.current_task = task.id
        self._save_state()

        try:
            result = self.agent.tools.execute(task.description)
            episode = Episode(
                task_id=task.id,
                input=task.description,
                output=result,
                success=True,
                timestamp=datetime.utcnow().isoformat(),
            )
            self._log_episode(episode)

            self.state.completed_tasks += 1
            self.state.status = AgentStatus.COMPLETED
            return True

        except Exception as exc:  
            episode = Episode(
                task_id=task.id,
                input=task.description,
                output=str(exc),
                success=False,
                timestamp=datetime.utcnow().isoformat(),
            )
            self._log_episode(episode)
            self.state.status = AgentStatus.FAILED
            return False

        finally:
            self.state.current_task = None
            self._save_state()

    def run_goal(self, goal: str, tasks: list[Task], stop_cfg: StopConfig | None = None) -> str:
        stop_cfg = stop_cfg or StopConfig()
        tracker = StopTracker(stop_cfg)

        completed: set[str] = set()
        queue = TaskQueue()
        queue.push_many(tasks)

        print(f"Goal received: {goal}")
        print(f"Tasks created: {len(tasks)}")

        while True:
            should, reason = tracker.should_stop(len(queue))
            if should:
                print(reason)
                return reason

            tracker.tick_iteration()

            task = queue.pop_ready(completed)
            if task is None:
                tracker.mark_no_progress()
                continue

            ok = self.run_once(task)
            if ok:
                completed.add(task.id)
                tracker.mark_progress()
                print(f"Tasks executed: {task.id}")
            else:
                tracker.mark_no_progress()

    def _save_state(self) -> None:
        with open(AUDIT_DIR / "state.json", "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, indent=2)

    def _log_episode(self, episode: Episode) -> None:
        with open(AUDIT_DIR / "episodes.jsonl", "a", encoding="utf-8") as f:
            f.write(episode.to_json() + "\n")
