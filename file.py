import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from stock import Stock


@dataclass
class CompletionRecord:
    task: str
    completed_at: str
    completed_by: str
    bags_added: Optional[int] = None

    def to_dict(self) -> dict:
        d = {
            "task": self.task,
            "completed_at": self.completed_at,
            "completed_by": self.completed_by,
        }
        if self.bags_added is not None:
            d["bags_added"] = self.bags_added
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "CompletionRecord":
        return cls(
            task=data["task"],
            completed_at=data["completed_at"],
            completed_by=data["completed_by"],
            bags_added=data.get("bags_added"),
        )


@dataclass
class AppState:
    task_states: dict  # TaskType.name (str) -> raw state dict
    history: list      # list[CompletionRecord]
    stock: Stock

    def to_dict(self) -> dict:
        return {
            "tasks": self.task_states,
            "history": [r.to_dict() for r in self.history],
            "stock": self.stock.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AppState":
        return cls(
            task_states=data.get("tasks", {}),
            history=[CompletionRecord.from_dict(r) for r in data.get("history", [])],
            stock=Stock.from_dict(data.get("stock", {})),
        )


class JsonFile:
    def __init__(self, path: str):
        self._path = Path(path)

    def load(self) -> AppState:
        if self._path.exists():
            with open(self._path) as f:
                return AppState.from_dict(json.load(f))
        return AppState.from_dict({})

    def save(self, state: AppState) -> None:
        with open(self._path, "w") as f:
            json.dump(state.to_dict(), f, indent=2)
