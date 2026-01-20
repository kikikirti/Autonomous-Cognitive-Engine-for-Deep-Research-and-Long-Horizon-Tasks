from __future__ import annotations

import re

from ace.core.quality.models import ReflectionResult


class ReflectorInterface:
    def reflect(self, task_text: str, result_text: str) -> ReflectionResult:
        raise NotImplementedError


class RuleBasedReflector(ReflectorInterface):
    

    def reflect(self, task_text: str, result_text: str) -> ReflectionResult:
        issues: list[str] = []
        improvements: list[str] = []
        score = 1.0

        txt = result_text.strip()
        if len(txt) < 120:
            score -= 0.35
            issues.append("Answer too short / low detail.")
            improvements.append("Add more evidence and a structured synthesis.")

        if "Stubbed web_search" in txt or "example.com/stub" in txt:
            score -= 0.30
            issues.append("Evidence looks like stub/demo data.")
            improvements.append("Broaden query or use internal memory for richer context.")

        has_citations_block = "Citations:" in txt
        has_numbered_refs = bool(re.search(r"\[\d+\]", txt))
        if not (has_citations_block and has_numbered_refs):
            score -= 0.25
            issues.append("Missing citation structure.")
            improvements.append("Ensure evidence is fused and cited as [1], [2], ...")

        redo = score < 0.55

        suggested_query = None
        if redo:
            
            suggested_query = f"{task_text} overview examples best practices"

        escalate = score < 0.40

        
        score = max(0.0, min(1.0, score))

        return ReflectionResult(
            score=score,
            issues=issues,
            improvements=improvements,
            redo=redo,
            suggested_query=suggested_query,
            escalate_to_human=escalate,
        )
