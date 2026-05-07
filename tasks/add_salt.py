from datetime import datetime
from typing import Optional

from chat import Chat
from file import CompletionRecord
from stock import Stock
from tasks.task import Task, TaskType


class AddSaltTask(Task):
    def __init__(self, stock: Stock, days_per_salt_bag: int, **kwargs):
        self.stock = stock
        self.days_per_salt_bag = days_per_salt_bag
        super().__init__(**kwargs)

    def get_callbacks(self) -> dict:
        return {**super().get_callbacks(), "bags": self.handle_followup_tap}

    async def send_reminder(self) -> None:
        await self.chat.send(
            f"<b>Podsetnik za odrzavanje</b>\n\nZadatak: <b>{self.description}</b>",
            reply_markup=Chat.done_keyboard(f"done:{self.name.name}"),
        )

    async def handle_done_tap(self, query, user_name: str, value: Optional[int] = None) -> None:
        await query.edit_message_text(
            f"<b>Koliko kesa soli si dodao?</b>\n\n<i>{user_name} odgovara...</i>",
            parse_mode="HTML",
            reply_markup=Chat.bags_keyboard(),
        )
        return None

    async def handle_followup_tap(self, query, user_name: str, value: Optional[int] = None) -> dict:
        return {"bags": value}

    async def complete_task(self, completed_by: str, options: dict) -> str:
        bags = options.get("bags", 0)
        if bags <= 0:
            return "Navedite broj kesa: <code>/done bags=N</code>"

        now = datetime.now()
        self.complete(completed_by)
        self.schedule_next(now, bags * self.days_per_salt_bag)
        self.stock.decrement(bags)

        self.app_state.history.append(CompletionRecord(
            task=self.name.name,
            completed_at=now.isoformat(),
            completed_by=completed_by,
            bags_added=bags,
        ))
        self._save()

        return (
            f"Dodato {bags} kesa soli.\n"
            f"Sledeci zadatak: <b>{self.next_due.strftime('%d.%m.%Y')}</b>\n"
            f"Zalihe soli: <b>{self.stock.salt_bags} kesa</b>"
        )
