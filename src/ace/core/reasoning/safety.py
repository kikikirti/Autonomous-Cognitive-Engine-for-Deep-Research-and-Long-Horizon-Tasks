from __future__ import annotations

from dataclasses import dataclass

from ace.core.reasoning.action_schema import ActionPlan


@dataclass
class SafetyPolicy:
    
    blocked_keywords: tuple[str, ...] = (
        "robot",
        "weapon",
        "explosive",
        "malware",
        "hack",
    )

    
    approval_keywords: tuple[str, ...] = (
        "publish",
        "post",
        "send email",
        "upload",
        "deploy",
        "delete",
        "overwrite",
    )

    def check(self, task_text: str, plan: ActionPlan) -> ActionPlan:
        lowered = task_text.lower()

        
        if any(k in lowered for k in self.blocked_keywords):
            return ActionPlan(
                action="STOP",
                rationale="Safety gate: out-of-scope/blocked request detected.",
                stop_reason="Blocked by safety policy",
                requires_approval=False,
            )

        
        if any(k in lowered for k in self.approval_keywords):
            plan.requires_approval = True

        
        if plan.action == "TOOL_CALL" and plan.tool_call:
            if plan.tool_call.name == "file_writer":
                path = str(plan.tool_call.input.get("path", ""))
                if path.startswith("..") or path.startswith("/") or ":\\" in path:
                    return ActionPlan(
                        action="STOP",
                        rationale="Safety gate: invalid file path requested.",
                        stop_reason="Blocked path traversal / absolute path",
                    )

        return plan
