from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ace.core.agent import Agent
from ace.core.models import AgentState, AgentStatus, Episode, Task
from ace.core.queue import TaskQueue
from ace.core.rag.fusion import RAGFusion
from ace.core.rag.pipeline import RAGPipeline
from ace.core.rag.retrievers import InternalRetriever, WebRetriever
from ace.core.stop import StopConfig, StopTracker
from ace.core.tool_schemas import ToolRequest

AUDIT_DIR = Path("audit")
AUDIT_DIR.mkdir(exist_ok=True)


class AgentStateMachine:
    def __init__(self, agent: Agent):
        self.agent = agent
        self.state = AgentState(status=AgentStatus.IDLE, 
                                current_task=None, 
                                completed_tasks=0)

    def run_once(self, task: Task) -> bool:
        self.state.status = AgentStatus.RUNNING
        self.state.current_task = task.id
        self._save_state()

        
        self.agent.memory.system.add_to_stm("task", task.description, {"task_id": task.id})

        try:
            
            pipeline = RAGPipeline(
                web_retriever=WebRetriever(self.agent.tools),
                internal_retriever=InternalRetriever(self.agent.memory.system),
                fusion=RAGFusion(max_chunks=8),
            )
            rag = pipeline.run(query=task.description, limit=5)

            result_text = rag.answer

            
            for idx, ch in enumerate(rag.fused, start=1):
                self.agent.memory.system.remember_long_term(
                    record_id=f"retrieval:{task.id}:{idx}:{ch.citation.timestamp}",
                    text=ch.text,
                    tags=["retrieval", "chunk", ch.citation.source],
                    metadata={
                        "task_id": task.id,
                        "source": ch.citation.source,
                        "source_id": ch.citation.source_id,
                        "confidence": ch.citation.confidence,
                        "timestamp": ch.citation.timestamp,
                    },
                )

            
            chunks_jsonl = "\n".join([c.to_json() for c in rag.fused])

            self.agent.tools.execute(
                ToolRequest(
                    name="file_writer",
                    input={"path": f"task_{task.id}/chunks.jsonl", "content": chunks_jsonl},
                    trace_id=f"{task.id}-chunks",
                )
            )

            self.agent.tools.execute(
                ToolRequest(
                    name="file_writer",
                    input={"path": f"task_{task.id}/answer.md", "content": result_text},
                    trace_id=f"{task.id}-answer",
                )
            )

            
            if task.id == "t4":
                self.agent.tools.execute(
                    ToolRequest(
                        name="file_writer",
                        input={
                            "path": "summary.md", 
                            "content": f"# Final Output\n\n{result_text}\n",
                            },
                        trace_id=f"{task.id}-write",
                    )
                )

            
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
                tags=["episode", "rag_run"],
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

    def run_goal(self, 
                 goal: str, 
                 tasks: list[Task], 
                 stop_cfg: StopConfig | None = None
                 ) -> str:
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
