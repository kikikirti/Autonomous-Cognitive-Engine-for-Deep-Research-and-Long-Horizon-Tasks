from __future__ import annotations

from ace.core.reasoning.action_schema import ActionPlan, ToolCall
from ace.core.reasoning.reasoner_interface import ReasonerInterface
from ace.core.reasoning.safety import SafetyPolicy


class RuleBasedReasoner(ReasonerInterface):
    

    def __init__(self, safety: SafetyPolicy | None = None) -> None:
        self.safety = safety or SafetyPolicy()

    def plan(self, task_text: str) -> ActionPlan:
        t = task_text.lower().strip()

        
        plan = ActionPlan(action="THINK", rationale="Default safe reasoning step.")

        if any(k in t for k in ["ask human", "need approval", "confirm with"]):
            plan = ActionPlan(
                action="ASK_HUMAN",
                rationale="Task indicates human input is required.",
                ask="Please clarify the requirement / provide approval to proceed.",
            )

        elif any(k in t for k in ["collect", "sources", "evidence", "papers", "search"]):
            plan = ActionPlan(
                action="TOOL_CALL",
                rationale="Need evidence; use web search tool to retrieve sources.",
                tool_call=ToolCall(name="web_search", input={"query": task_text, "limit": 5}),
            )

        elif any(k in t for k in ["clarify", "scope", "assumption"]):
            plan = ActionPlan(
                action="THINK",
                rationale="Clarification tasks are handled by internal reasoning + context.",
            )

        elif any(k in t for k in ["stop", "halt"]):
            plan = ActionPlan(
                action="STOP",
                rationale="Task explicitly requests stop.",
                stop_reason="User requested stop",
            )

        
        return self.safety.check(task_text, plan)
