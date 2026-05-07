from datetime import datetime
from typing import Optional

from chat import Chat
from file import CompletionRecord
from tasks.task import Task, TaskType


class GarageDrainTask(Task):
    async def send_reminder(self) -> None:
        await self.chat.send(
            f"<b>Podsetnik za odrzavanje</b>\n\nZadatak: <b>{self.description}</b>",
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

        return (
            f"Zadatak zavrsen.\n"
            f"Sledeci podsetnik: <b>{self.next_due.strftime('%d.%m.%Y')}</b>"
        )
