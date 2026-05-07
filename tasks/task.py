from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from chat import Chat

if TYPE_CHECKING:
    from file import JsonFile, AppState


class TaskType(Enum):
    ADD_SALT = "Dodaj tablete soli"
    CLEAN_GARAGE_DRAIN = "Ocisti garazni slivnik"
    LOW_SALT_STOCK = "Naruci tablete soli - zalihe su niske"


class Task(ABC):
    def __init__(
        self,
        chat: Chat,
        file: "JsonFile",
        app_state: "AppState",
        name: TaskType,
        description: str,
        interval: int,
        notification_resend_interval: float = 24,
        next_due: Optional[datetime] = None,
        pending: bool = False,
        last_completed: Optional[datetime] = None,
        last_completed_by: str = "",
        last_sent_notification: Optional[datetime] = None,
    ):
        self.chat = chat
        self.file = file
        self.app_state = app_state
        self.name = name
        self.description = description
        self.interval = interval
        self.notification_resend_interval = notification_resend_interval
        self.pending = pending
        self.last_completed = last_completed
        self.last_completed_by = last_completed_by
        self.next_due = next_due
        self.last_sent_notification = last_sent_notification

        if self.next_due is None:
            self.set_next_due()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _save(self) -> None:
        self.app_state.task_states[self.name.name] = self.to_dict()
        self.file.save(self.app_state)

    def mark_pending(self) -> None:
        self.pending = True
        self.last_sent_notification = datetime.now()
        self._save()

    def should_notify(self) -> bool:
        if not self.is_overdue():
            return False
        if self.last_sent_notification is None:
            return True
        return datetime.now() - self.last_sent_notification >= timedelta(hours=self.notification_resend_interval)

    # ── Abstract interface ────────────────────────────────────────────────────

    @abstractmethod
    async def send_reminder(self) -> None: ...

    @abstractmethod
    async def complete_task(self, completed_by: str, options: dict) -> str: ...

    @abstractmethod
    async def handle_done_tap(self, query, user_name: str, value: Optional[int] = None) -> Optional[dict]:
        """
        Called when the 'Zavrseno' button is tapped.
        Return a dict of options to complete immediately, or None if a follow-up
        keyboard is needed (and this method handles the message edit itself).
        """
        ...

    async def handle_followup_tap(self, query, user_name: str, value: Optional[int] = None) -> dict:
        """
        Called when a follow-up button (bag count, order count, etc.) is tapped.
        Return the options dict to pass to complete_task.
        Override in tasks that have a two-step flow.
        """
        return {}

    def get_callbacks(self) -> dict:
        """
        Return a routing dict of {callback_key: handler} for this task.
        Base implementation registers the 'Zavrseno' button for this task.
        Subclasses extend this to add follow-up handlers (bags, order, etc.).
        """
        return {f"done:{self.name.name}": self.handle_done_tap}

    # ── Scheduling helpers ────────────────────────────────────────────────────

    def set_next_due(
        self,
        from_date: Optional[datetime] = None,
        interval_days: Optional[int] = None,
        next_due: Optional[datetime] = None,
    ) -> None:
        if next_due is not None:
            self.next_due = next_due
            return
        if from_date is None:
            from_date = datetime.now()
        if interval_days is None:
            interval_days = self.interval
        self.next_due = from_date + timedelta(days=interval_days)

    def is_overdue(self) -> bool:
        if self.next_due is None:
            return True
        return datetime.now() >= self.next_due

    def schedule_next(self, from_date: datetime, interval_days: int) -> None:
        self.set_next_due(from_date=from_date, interval_days=interval_days)
        self.pending = False

    def complete(self, completed_by: str) -> None:
        self.last_completed = datetime.now()
        self.last_completed_by = completed_by
        self.pending = False

    def to_dict(self) -> dict:
        return {
            "next_due": self.next_due.isoformat() if self.next_due else None,
            "pending": self.pending,
            "last_completed": self.last_completed.isoformat() if self.last_completed else None,
            "last_completed_by": self.last_completed_by,
            "last_sent_notification": self.last_sent_notification.isoformat() if self.last_sent_notification else None,
        }

    def restore_from_dict(self, data: dict) -> None:
        if data.get("next_due"):
            self.next_due = datetime.fromisoformat(data["next_due"])
        self.pending = data.get("pending", False)
        if data.get("last_completed"):
            self.last_completed = datetime.fromisoformat(data["last_completed"])
        self.last_completed_by = data.get("last_completed_by", "")
        if data.get("last_sent_notification"):
            self.last_sent_notification = datetime.fromisoformat(data["last_sent_notification"])
