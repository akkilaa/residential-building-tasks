import json
import pytest
from datetime import datetime, timedelta
from pathlib import Path

from task import Task, TaskType, AddSaltTask, GarageDrainTask, LowSaltStockTask
from file import JsonFile, AppState
from stock import Stock
from scheduler import Scheduler

# ── Fakes ─────────────────────────────────────────────────────────────────────


class FakeChat:
    async def send(self, message, reply_markup=None):
        pass

    async def send_to_user(self, user_id, message):
        pass


def make_tasks() -> dict:
    chat = FakeChat()
    return {
        TaskType.ADD_SALT: AddSaltTask(
            chat=chat,
            name=TaskType.ADD_SALT,
            description=TaskType.ADD_SALT.value,
            interval=14,
        ),
        TaskType.CLEAN_GARAGE_DRAIN: GarageDrainTask(
            chat=chat,
            name=TaskType.CLEAN_GARAGE_DRAIN,
            description=TaskType.CLEAN_GARAGE_DRAIN.value,
            interval=30,
        ),
        TaskType.LOW_SALT_STOCK: LowSaltStockTask(
            chat=chat,
            name=TaskType.LOW_SALT_STOCK,
            description=TaskType.LOW_SALT_STOCK.value,
            interval=0,
        ),
    }


def make_scheduler(tmp_path: Path, state_filename: str = "bot_state.json") -> Scheduler:
    state_file = tmp_path / state_filename
    return Scheduler(
        tasks=make_tasks(),
        commands=[],
        chat=FakeChat(),
        file=JsonFile(str(state_file)),
        admin_user_id=1,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestSchedulerInitWithEmptyFile:
    """Scheduler starts with no existing state file."""

    def test_state_file_is_created_after_initialization(self, tmp_path):
        state_file = tmp_path / "bot_state.json"
        assert not state_file.exists()

        scheduler = make_scheduler(tmp_path)
        scheduler._ensure_task_state_initialized()

        assert state_file.exists()

    def test_all_configured_tasks_are_written_to_file(self, tmp_path):
        scheduler = make_scheduler(tmp_path)
        scheduler._ensure_task_state_initialized()

        data = json.loads((tmp_path / "bot_state.json").read_text())
        saved_task_names = set(data["tasks"].keys())

        assert saved_task_names == {"ADD_SALT", "CLEAN_GARAGE_DRAIN", "LOW_SALT_STOCK"}

    def test_initialization_returns_true_when_state_was_empty(self, tmp_path):
        scheduler = make_scheduler(tmp_path)
        result = scheduler._ensure_task_state_initialized()

        assert result is True


class TestSchedulerInitWithExistingFile:
    """Scheduler starts with a pre-populated state file."""

    def _write_state(self, tmp_path: Path, next_due_offset_days: int = 10) -> dict:
        next_due = (datetime.now() + timedelta(days=next_due_offset_days)).isoformat()
        last_completed = datetime.now().isoformat()
        state = {
            "tasks": {
                "ADD_SALT": {
                    "next_due": next_due,
                    "pending": False,
                    "last_completed": last_completed,
                    "last_completed_by": "Marko",
                },
                "CLEAN_GARAGE_DRAIN": {
                    "next_due": next_due,
                    "pending": False,
                    "last_completed": last_completed,
                    "last_completed_by": "Ana",
                },
                "LOW_SALT_STOCK": {
                    "next_due": None,
                    "pending": False,
                    "last_completed": last_completed,
                    "last_completed_by": "Ana",
                },
            },
            "history": [],
            "stock": {"salt_bags": 5, "low_stock_threshold": 2},
        }
        (tmp_path / "bot_state.json").write_text(json.dumps(state))
        return state

    def test_initialization_returns_false_when_state_is_complete(self, tmp_path):
        self._write_state(tmp_path)
        scheduler = make_scheduler(tmp_path)
        result = scheduler._ensure_task_state_initialized()

        assert result is False
