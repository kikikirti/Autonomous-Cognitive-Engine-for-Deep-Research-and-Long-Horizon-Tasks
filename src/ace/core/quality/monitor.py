from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class MonitorConfig:
    max_redos_per_task: int = 2
    low_score_threshold: float = 0.55
    low_score_streak_limit: int = 2
    repeated_query_limit: int = 2


@dataclass
class MonitorState:
    last_queries: deque[str] = field(default_factory=lambda: deque(maxlen=10))
    low_score_streak: int = 0


class QualityMonitor:
    def __init__(self, cfg: MonitorConfig | None = None) -> None:
        self.cfg = cfg or MonitorConfig()
        self.state = MonitorState()

    def observe_query(self, q: str) -> bool:
        q_norm = q.strip().lower()
        self.state.last_queries.append(q_norm)
        count = sum(1 for x in self.state.last_queries if x == q_norm)
        return count > self.cfg.repeated_query_limit

    def observe_score(self, score: float) -> bool:
        
        if score < self.cfg.low_score_threshold:
            self.state.low_score_streak += 1
        else:
            self.state.low_score_streak = 0
        return self.state.low_score_streak >= self.cfg.low_score_streak_limit
