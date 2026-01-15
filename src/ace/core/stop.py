from __future__ import annotations

from dataclasses import dataclass


@dataclass
class StopConfig:
    max_iterations: int = 25
    max_no_progress: int = 5


@dataclass
class StopTracker:
    cfg: StopConfig
    iterations: int = 0
    no_progress_steps: int = 0

    def tick_iteration(self) -> None:
        self.iterations += 1

    def mark_progress(self) -> None:
        self.no_progress_steps = 0

    def mark_no_progress(self) -> None:
        self.no_progress_steps += 1

    def should_stop(self, queue_len: int) -> tuple[bool, str]:
        if queue_len == 0:
            return True, "Halted: All tasks completed"
        if self.iterations >= self.cfg.max_iterations:
            return True, "Halted: Max iterations reached"
        if self.no_progress_steps >= self.cfg.max_no_progress:
            return True, "Halted: No progress"
        return False, ""
