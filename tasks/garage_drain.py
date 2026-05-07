from datetime import datetime
from typing import Optional

import i18n
from chat import Chat
from file import CompletionRecord
from tasks.task import Task, TaskType


class GarageDrainTask(Task):
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

        self.app_state.history.append(CompletionRecord(
            task=self.name.name,
            completed_at=now.isoformat(),
            completed_by=completed_by,
        ))
        self._save()

        return i18n.t("tasks.clean_garage_drain.complete", next_due=self.next_due.strftime("%d.%m.%Y"))
