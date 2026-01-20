from __future__ import annotations

from dataclasses import dataclass

from ace.core.memory_store import SQLiteMemoryStore
from ace.core.memory_system import EpisodicMemory, MemorySystem, ShortTermMemory


@dataclass
class Memory:
    system: MemorySystem

    @classmethod
    def create_default(cls) -> "Memory":
        stm = ShortTermMemory(max_items=20)
        stm.load()
        episodic = EpisodicMemory(episodes_path="audit/episodes.jsonl")
        ltm = SQLiteMemoryStore(db_path="data/memory.db")
        return cls(system=MemorySystem(stm=stm, episodic=episodic, ltm=ltm))
