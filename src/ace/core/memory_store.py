from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class MemoryRecord:
    id: str
    text: str
    created_at: float
    tags: list[str]
    metadata: dict[str, Any]
    embedding: list[float] | None = None  # embedding-ready placeholder


class SQLiteMemoryStore:
    def __init__(self, db_path: str = "data/memory.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path.as_posix())

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS ltm_records (
                    id TEXT PRIMARY KEY,
                    text TEXT NOT NULL,
                    created_at REAL NOT NULL,
                    tags TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    embedding TEXT
                )
                """
            )

    def upsert(self, record: MemoryRecord) -> None:
        with self._connect() as con:
            con.execute(
                """
                INSERT INTO ltm_records (id, text, created_at, tags, metadata, embedding)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    text=excluded.text,
                    created_at=excluded.created_at,
                    tags=excluded.tags,
                    metadata=excluded.metadata,
                    embedding=excluded.embedding
                """,
                (
                    record.id,
                    record.text,
                    record.created_at,
                    json.dumps(record.tags),
                    json.dumps(record.metadata),
                    json.dumps(record.embedding) if record.embedding is not None else None,
                ),
            )

    def add_text(
            self, 
            record_id: str, 
            text: str, 
            tags: list[str] | None = None, 
            metadata: dict[str, Any] | None = None
                 ) -> None:
        rec = MemoryRecord(
            id=record_id,
            text=text,
            created_at=time.time(),
            tags=tags or [],
            metadata=metadata or {},
            embedding=None,
        )
        self.upsert(rec)

    def search(self, query: str, limit: int = 5) -> list[MemoryRecord]:
        query = query.strip()
        if not query:
            return []

        with self._connect() as con:
            cur = con.execute(
                """
                SELECT id, text, created_at, tags, metadata, embedding
                FROM ltm_records
                WHERE text LIKE ?
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (f"%{query}%", limit),
            )
            rows = cur.fetchall()

        out: list[MemoryRecord] = []
        for rid, text, created_at, tags, metadata, embedding in rows:
            out.append(
                MemoryRecord(
                    id=rid,
                    text=text,
                    created_at=float(created_at),
                    tags=json.loads(tags),
                    metadata=json.loads(metadata),
                    embedding=json.loads(embedding) if embedding else None,
                )
            )
        return out

    def recent(self, limit: int = 5) -> list[MemoryRecord]:
        with self._connect() as con:
            cur = con.execute(
                """
                SELECT id, text, created_at, tags, metadata, embedding
                FROM ltm_records
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cur.fetchall()

        out: list[MemoryRecord] = []
        for rid, text, created_at, tags, metadata, embedding in rows:
            out.append(
                MemoryRecord(
                    id=rid,
                    text=text,
                    created_at=float(created_at),
                    tags=json.loads(tags),
                    metadata=json.loads(metadata),
                    embedding=json.loads(embedding) if embedding else None,
                )
            )
        return out
