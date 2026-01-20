from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Any


@dataclass
class Citation:
    source: str
    source_id: str
    timestamp: str
    snippet: str
    confidence:float
    def to_dict(self) -> dict[str, Any] :
        return asdict(self)


@dataclass
class RetrievedChunk:
    text: str
    citation:Citation
    def to_json(self) -> str:
        return json.dumps(
            {"text": self.text, "citation": self.citation.to_dict()},
            ensure_ascii=False,
        )