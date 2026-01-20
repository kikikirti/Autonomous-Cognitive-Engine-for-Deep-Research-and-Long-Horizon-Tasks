from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from ace.core.agent import Agent
from ace.core.models import AgentState, AgentStatus, Episode, Task
from ace.core.quality.monitor import MonitorConfig, QualityMonitor
from ace.core.quality.reflector import RuleBasedReflector
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
        self.state = AgentState(
            status=AgentStatus.IDLE,
            current_task=None,
            completed_tasks=0,
        )
        self.reflector_engine = RuleBasedReflector()
        self.monitor = QualityMonitor(MonitorConfig())

    def run_once(self, task: Task) -> bool:
        self.state.status = AgentStatus.RUNNING
        self.state.current_task = task.id
        self._save_state()

        self.agent.memory.system.add_to_stm("task", task.description, {"task_id": task.id})

        try:
            plan = self.agent.reasoner.plan(task.description)

            self.agent.memory.system.add_to_stm(
                "plan",
                str(plan),
                {"task_id": task.id},
            )

            if getattr(plan, "requires_approval", False):
                raise RuntimeError("Approval required by safety policy for this action.")

            if plan.action == "STOP":
                raise RuntimeError(plan.stop_reason or "Stopped by reasoner policy.")

            if plan.action == "ASK_HUMAN":
                raise RuntimeError(plan.ask or "Human input required by reasoner policy.")

            redos = 0
            query = task.description
            result_text: str = ""

            while True:
                repeated = self.monitor.observe_query(query)

                if plan.action == "TOOL_CALL" and plan.tool_call is not None:
                    req = ToolRequest(
                        name=plan.tool_call.name,
                        input=plan.tool_call.input,
                        trace_id=f"{task.id}-policy",
                    )
                    resp = self.agent.tools.execute(req)
                    if not resp.ok:
                        msg = "Tool failed"
                        if resp.error is not None:
                            msg = resp.error.message
                        raise RuntimeError(msg)

                    result_text = str(resp.output)

                else:
                    pipeline = RAGPipeline(
                        web_retriever=WebRetriever(self.agent.tools),
                        internal_retriever=InternalRetriever(self.agent.memory.system),
                        fusion=RAGFusion(max_chunks=8),
                    )
                    rag = pipeline.run(query=query, limit=5)
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
                            input={
                                "path": f"task_{task.id}/chunks.jsonl",
                                "content": chunks_jsonl,
                            },
                            trace_id=f"{task.id}-chunks",
                        )
                    )

                    self.agent.tools.execute(
                        ToolRequest(
                            name="file_writer",
                            input={
                                "path": f"task_{task.id}/answer.md",
                                "content": result_text,
                            },
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

                reflection = self.reflector_engine.reflect(task.description, result_text)

                self.agent.memory.system.add_to_stm(
                    "reflection",
                    json.dumps(reflection.to_dict(), ensure_ascii=False),
                    {"task_id": task.id},
                )

                self.agent.memory.system.remember_long_term(
                    record_id=f"reflection:{task.id}:{datetime.utcnow().isoformat()}",
                    text=json.dumps(reflection.to_dict(), ensure_ascii=False),
                    tags=["reflection", "quality"],
                    metadata={"task_id": task.id, "score": reflection.score},
                )

                low_streak = self.monitor.observe_score(reflection.score)

                if repeated or low_streak or reflection.escalate_to_human:
                    raise RuntimeError(
                        "Escalate to human: repeated queries or low-quality streak detected."
                    )

                if reflection.redo and redos < self.monitor.cfg.max_redos_per_task:
                    redos += 1
                    query = reflection.suggested_query or f"{query} best practices"

                    self.agent.memory.system.add_to_stm(
                        "redo",
                        f"Redo #{redos} with query: {query}",
                        {"task_id": task.id},
                    )
                    continue

                break

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
                tags=["episode", "policy_run"],
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

    def run_goal(
        self,
        goal: str,
        tasks: list[Task],
        stop_cfg: StopConfig | None = None,
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
                # ✅ Milestone 7 loop breaker: don't stall the whole run on one failure.
                completed.add(task.id)
                tracker.mark_progress()
                print(f"Task failed (skipped): {task.id}")
                self.agent.memory.system.add_to_stm(
                    "skip",
                    f"Skipped failed task: {task.id}",
                    {"task_id": task.id},
                )

    def _save_state(self) -> None:
        with open(AUDIT_DIR / "state.json", "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, indent=2)

    def _log_episode(self, episode: Episode) -> None:
        with open(AUDIT_DIR / "episodes.jsonl", "a", encoding="utf-8") as f:
            f.write(episode.to_json() + "\n")
