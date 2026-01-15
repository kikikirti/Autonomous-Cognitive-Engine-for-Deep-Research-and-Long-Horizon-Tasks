from dataclasses import dataclass


@dataclass
class Reflector:
    def evaluate(self, result: str) -> dict:
        return {"quality":"unknown", "notes":"Milestone 0 placeholder"}