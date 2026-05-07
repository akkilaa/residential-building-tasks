from abc import ABC, abstractmethod

from telegram import Update, BotCommand
from telegram.ext import ContextTypes

import i18n
from chat import Chat
from file import AppState


class Command(ABC):
    name: str

    @property
    def description(self) -> str:
        return i18n.t(f"commands.{self.name}.description")

    @abstractmethod
    async def handle(
        self,
        update: Update,
        ctx: ContextTypes.DEFAULT_TYPE,
        scheduler,
        app_state: AppState,
    ) -> None:
        raise NotImplementedError

    def to_bot_command(self) -> BotCommand:
        return BotCommand(command=self.name, description=self.description)


class StartCommand(Command):
    name = "start"

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE, scheduler, app_state) -> None:
        await update.message.reply_text(i18n.t("commands.start.message"))


class DoneCommand(Command):
    name = "done"

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE, scheduler, app_state) -> None:
        tasks = [t for t in scheduler.tasks.values()]
        if not tasks:
            await update.message.reply_text(i18n.t("commands.done.no_tasks"))
            return
        await update.message.reply_text(
            i18n.t("commands.done.prompt"),
            parse_mode="HTML",
            reply_markup=Chat.tasks_keyboard(tasks),
        )


class StatusCommand(Command):
    name = "status"

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE, scheduler, app_state) -> None:
        await update.message.reply_text(scheduler.get_status(), parse_mode="HTML")


class RemindCommand(Command):
    name = "remind"

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE, scheduler, app_state) -> None:
        await scheduler.send_overdue_reminders()
        await update.message.reply_text(i18n.t("commands.remind.sent"))


class GetStock(Command):
    name = "stanje"

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE, scheduler, app_state) -> None:
        await update.message.reply_text(
            i18n.t("commands.stock.status", bags=app_state.stock.salt_bags),
            parse_mode="HTML",
        )
