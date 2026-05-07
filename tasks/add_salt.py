from datetime import datetime
from typing import Optional

import i18n
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
            i18n.t("tasks.generic_reminder", description=self.description),
            reply_markup=Chat.done_keyboard(f"done:{self.name.name}"),
        )

    async def handle_done_tap(self, query, user_name: str, value: Optional[int] = None) -> None:
        await query.edit_message_text(
            i18n.t("tasks.add_salt.followup_prompt", user_name=user_name),
            parse_mode="HTML",
            reply_markup=Chat.bags_keyboard(),
        )
        return None

    async def handle_followup_tap(self, query, user_name: str, value: Optional[int] = None) -> dict:
        return {"bags": value}

    async def complete_task(self, completed_by: str, options: dict) -> str:
        bags = options.get("bags", 0)
        if bags <= 0:
            return i18n.t("tasks.add_salt.bags_required")

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

        return i18n.t(
            "tasks.add_salt.complete",
            bags=bags,
            next_due=self.next_due.strftime("%d.%m.%Y"),
            stock=self.stock.salt_bags,
        )
