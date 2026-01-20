from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from ace.core.memory_store import SQLiteMemoryStore


@dataclass
class ShortTermMemory:
    max_items: int = 20
    items: list[dict[str, Any]] = field(default_factory=list)
    path: Path=Path("data/stm.json")
    
    def load(self) -> None:
        if self.path.exists():
            try:
                self.items = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self.items = []
    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.items, indent=2),encoding="utf-8")

    def add(self, item: dict[str, Any]) -> None:
        self.items.append(item)
        if len(self.items) > self.max_items:
            self.items = self.items[-self.max_items :]
        self.save()

    def snapshot(self) -> list[dict[str, Any]]:
        return list(self.items)


class EpisodicMemory:
    def __init__(self, episodes_path: str = "audit/episodes.jsonl") -> None:
        self.path = Path(episodes_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def append_line(self, line: str) -> None:
        with open(self.path, "a", encoding="utf-8") as f:
            f.write(line.rstrip() + "\n")

    def load_recent(self, limit: int = 20) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        lines = self.path.read_text(encoding="utf-8").splitlines()
        lines = lines[-limit:]
        out: list[dict[str, Any]] = []
        for ln in lines:
            try:
                out.append(json.loads(ln))
            except json.JSONDecodeError:
                continue
        return out


@dataclass
class MemorySystem:
    stm: ShortTermMemory
    episodic: EpisodicMemory
    ltm: SQLiteMemoryStore

    def add_to_stm(self, kind: str, content: str, meta: dict[str, Any] | None = None) -> None:
        self.stm.add({"kind": kind, "content": content, "meta": meta or {}})

    def remember_long_term(
            self, 
            record_id: str, 
            text: str, 
            tags: list[str] | None = None, 
            metadata: dict[str, Any] | None = None
            ) -> None:
        self.ltm.add_text(record_id=record_id, text=text, tags=tags, metadata=metadata)

    def recall_long_term(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        recs = self.ltm.search(query=query, limit=limit)
        return [{"id": r.id, "text": r.text, "tags": r.tags, "metadata": r.metadata} for r in recs]
