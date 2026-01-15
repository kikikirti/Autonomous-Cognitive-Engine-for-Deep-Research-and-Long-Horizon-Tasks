from dataclasses import dataclass


@dataclass
class ToolExecutor:
    def execute(self,instruction: str) -> str:
        return f"Executed {instruction}"