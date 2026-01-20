from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ace.core.agent import Agent
from ace.core.models import AgentState, AgentStatus, Episode, Task
from ace.core.queue import TaskQueue
from ace.core.stop import StopConfig, StopTracker
from ace.core.tool_schemas import ToolRequest

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

        
        self.agent.memory.system.add_to_stm("task", task.description, {"task_id": task.id})

        try:
            req = ToolRequest(
                name="web_search",
                input={"query": task.description},
                trace_id=task.id,
            )

            resp = self.agent.tools.execute(req)
            if not resp.ok:
                raise RuntimeError(resp.error.message if resp.error else "Tool failed")

            result_text = str(resp.output)

            
            if task.id == "t4":
                write_req = ToolRequest(
                    name="file_writer",
                    input={"path": "summary.md", "content": f"# Final Output\n\n{result_text}\n"},
                    trace_id=f"{task.id}-write",
                )
                self.agent.tools.execute(write_req)

            episode = Episode(
                task_id=task.id,
                input=task.description,
                output=result_text,
                success=True,
                timestamp=datetime.utcnow().isoformat(),
            )
            self._log_episode(episode)

            
            self.agent.memory.system.add_to_stm("result", result_text, {"task_id": task.id})

            
            self.agent.memory.system.remember_long_term(
                record_id=f"episode:{task.id}:{episode.timestamp}",
                text=f"Task: {task.description}\nOutput: {result_text}",
                tags=["episode", "tool_run"],
                metadata={"task_id": task.id, "success": True},
            )

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

            
            self.agent.memory.system.add_to_stm("error", str(exc), {"task_id": task.id})

            
            self.agent.memory.system.remember_long_term(
                record_id=f"error:{task.id}:{episode.timestamp}",
                text=f"Task: {task.description}\nError: {str(exc)}",
                tags=["error", "episode"],
                metadata={"task_id": task.id, "success": False},
            )

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

        
        self.agent.memory.system.add_to_stm("goal", goal)

        while True:
            should, reason = tracker.should_stop(len(queue))
            if should:
                print(reason)

                
                self.agent.memory.system.add_to_stm("halt", reason)
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
