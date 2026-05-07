import asyncio
import logging

from tasks import TaskType
from chat import Chat

logger = logging.getLogger(__name__)


class Scheduler:
    def __init__(
        self,
        tasks: dict,
        commands: list,
        chat: Chat,
        admin_user_id: int,
        check_interval: int = 3600,
    ):
        self.tasks = tasks
        self.commands = commands
        self.chat = chat
        self.admin_user_id = admin_user_id
        self.check_interval = check_interval

    # ── Scheduler loop ────────────────────────────────────────────────────────

    async def start(self) -> None:
        logger.info("Scheduler started.")
        await self.chat.send("<b>Zdravo!</b>\n\nBot je pokrenut.")
        while True:
            await self.check_due()
            await asyncio.sleep(self.check_interval)

    async def check_due(self) -> None:
        for task_type, task in self.tasks.items():
            if task.should_notify():
                task.mark_pending()
                await task.send_reminder()
                logger.info(f"Task {task_type.name} overdue, notification sent.")

    # ── Reminders ─────────────────────────────────────────────────────────────

    async def send_overdue_reminders(self) -> None:
        pending = [t for t in self.tasks.values() if t.pending]
        if not pending:
            await self.chat.send("Nema aktivnih zadataka.")
            return
        for task in pending:
            await task.send_reminder()


    # ── Status ────────────────────────────────────────────────────────────────

    def get_status(self) -> str:
        lines = ["<b>Status zadataka</b>\n"]
        for task_type, task in self.tasks.items():
            if task_type == TaskType.LOW_SALT_STOCK:
                continue
            due_str = task.next_due.strftime("%d.%m.%Y") if task.next_due else "nije zakazano"
            overdue = " (PREKORACENO)" if task.is_overdue() else ""
            pending_str = " — ceka potvrdu" if task.pending else ""
            lines.append(f"• <b>{task.description}</b>: {due_str}{overdue}{pending_str}")

        alert = self.tasks.get(TaskType.LOW_SALT_STOCK)
        stock_bags = alert.stock.salt_bags if alert else 0
        low_str = " — NARUCI!" if alert and alert.pending else ""
        lines.append(f"\nZalihe soli: <b>{stock_bags} kesa</b>{low_str}")
        return "\n".join(lines)
