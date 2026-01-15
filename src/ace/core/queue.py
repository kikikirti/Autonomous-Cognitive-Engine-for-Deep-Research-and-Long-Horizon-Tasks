from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TaskQueue:
    _items: list[str] = field(default_factory=list)

    def push_many(self, tasks: list[str]) -> None:
        self._items.extend(tasks)

    def pop(self) -> str | None:
        return self._items.pop(0) if self._items else None

    def __len__(self) -> int:
        return len(self._items)
