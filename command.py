from abc import ABC, abstractmethod

from telegram import Update
from telegram.ext import ContextTypes

from chat import Chat
from file import AppState


class Command(ABC):
    name: str
    description: str

    @abstractmethod
    async def handle(
        self,
        update: Update,
        ctx: ContextTypes.DEFAULT_TYPE,
        scheduler,
        app_state: AppState,
    ) -> None:
        raise NotImplementedError


class StartCommand(Command):
    name = "start"
    description = "Pokretanje bota i prikaz komandi"

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE, scheduler, app_state) -> None:
        await update.message.reply_text(
            "Bot je aktivan!\n\n"
            "Komande:\n"
            "  /done — oznaci zadatak kao zavrsen\n"
            "  /done bags=3 — dodavanje soli (3 kese)\n"
            "  /status — prikazi status svih zadataka\n"
            "  /remind — posalji podsetnik odmah (samo admin)",
        )


class DoneCommand(Command):
    name = "done"
    description = "Prikazi zadatke koji cekaju potvrdu"

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE, scheduler, app_state) -> None:
        tasks = [t for t in scheduler.tasks.values() if t.interval > 0 or t.pending]
        if not tasks:
            await update.message.reply_text("Nema dostupnih zadataka.")
            return
        await update.message.reply_text(
            "<b>Koji zadatak si zavrsio?</b>",
            parse_mode="HTML",
            reply_markup=Chat.tasks_keyboard(tasks),
        )


class StatusCommand(Command):
    name = "status"
    description = "Prikazi status svih zadataka i zalihe"

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE, scheduler, app_state) -> None:
        await update.message.reply_text(scheduler.get_status(), parse_mode="HTML")


class RemindCommand(Command):
    name = "remind"
    description = "Posalji podsetnik odmah (samo admin)"

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE, scheduler, app_state) -> None:
        await scheduler.send_overdue_reminders()
        await update.message.reply_text("Podsetnici poslati grupi.")

class GetStock(Command):
    name = "stanje"
    description = "Posalji stanje zaliha"

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE, scheduler, app_state) -> None:
        stock = app_state.stock
        await update.message.reply_text(
            f"<b>Stanje zaliha</b>\n\n"
            f"So (kese): <b>{stock.salt_bags}</b>\n",
            parse_mode="HTML",
        )
