from datetime import datetime
from typing import Optional

import i18n
from chat import Chat
from file import CompletionRecord
from stock import Stock
from tasks.task import Task, TaskType


class ChangeWaterFilterTask(Task):
    def __init__(self, stock: Stock, **kwargs):
        self.stock = stock
        super().__init__(**kwargs)

    async def send_reminder(self) -> None:
        await self.chat.send(
            i18n.t("tasks.generic_reminder", description=self.description),
            reply_markup=Chat.done_keyboard(f"done:{self.name.name}"),
        )

    async def handle_done_tap(self, query, user_name: str, value: Optional[int] = None) -> dict:
        return {}

    async def complete_task(self, completed_by: str, options: dict) -> str:
        now = datetime.now()
        self.complete(completed_by)
        self.schedule_next(now, self.interval)
        self.stock.decrement_filters()

        self.app_state.history.append(CompletionRecord(
            task=self.name.name,
            completed_at=now.isoformat(),
            completed_by=completed_by,
        ))
        self._save()

        return i18n.t(
            "tasks.change_water_filter.complete",
            next_due=self.next_due.strftime("%d.%m.%Y"),
            filters=self.stock.filters,
        )
