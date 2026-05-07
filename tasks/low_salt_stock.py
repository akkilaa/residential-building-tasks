from datetime import datetime
from typing import Optional

import i18n
from chat import Chat
from file import CompletionRecord
from stock import Stock
from tasks.task import Task, TaskType


class LowSaltStockTask(Task):
    def __init__(self, stock: Stock, **kwargs):
        self.stock = stock
        super().__init__(**kwargs)

    def is_overdue(self) -> bool:
        return self.stock.is_low()

    def get_callbacks(self) -> dict:
        return {**super().get_callbacks(), "order": self.handle_followup_tap}

    async def send_reminder(self) -> None:
        await self.chat.send(
            i18n.t("tasks.low_salt_stock.alert", bags=self.stock.salt_bags),
            reply_markup=Chat.done_keyboard(f"done:{self.name.name}"),
        )

    async def handle_done_tap(self, query, user_name: str, value: Optional[int] = None) -> None:
        await query.edit_message_text(
            i18n.t("tasks.low_salt_stock.followup_prompt", user_name=user_name),
            parse_mode="HTML",
            reply_markup=Chat.order_keyboard(),
        )
        return None

    async def handle_followup_tap(self, query, user_name: str, value: Optional[int] = None) -> dict:
        return {"bags": value}

    async def complete_task(self, completed_by: str, options: dict) -> str:
        bags = options.get("bags", 0)
        if bags > 0:
            self.stock.add(bags)
        self.complete(completed_by)

        self.app_state.history.append(CompletionRecord(
            task=self.name.name,
            completed_at=datetime.now().isoformat(),
            completed_by=completed_by,
            bags_added=bags if bags > 0 else None,
        ))
        self._save()

        return i18n.t("tasks.low_salt_stock.complete", stock=self.stock.salt_bags)
