#!/usr/bin/env python3
import asyncio
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from datetime import datetime
import i18n
from tasks import TaskType, AddSaltTask, GarageDrainTask, LowSaltStockTask, ChangeWaterFilterTask
from chat import TelegramChat
from command import StartCommand, DoneCommand, StatusCommand, RemindCommand, GetStock
from file import JsonFile, AppState
from scheduler import Scheduler
from callback_router import CallbackRouter

# ─── CONFIG ──────────────────────────────────────────────────────────────────

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "-1001234567890"))
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID", "123456789"))
STATE_FILE = os.getenv("STATE_FILE", "bot_state.json")

DAYS_PER_SALT_BAG = int(os.getenv("DAYS_PER_SALT_BAG", "14"))
SALT_LOW_STOCK_THRESHOLD = int(os.getenv("SALT_LOW_STOCK_THRESHOLD", "2"))
SALT_INITIAL_STOCK = int(os.getenv("SALT_INITIAL_STOCK", "10"))
SCHEDULER_CHECK_INTERVAL = int(os.getenv("SCHEDULER_CHECK_INTERVAL", "3600"))
GARAGE_DRAIN_INTERVAL_DAYS = int(os.getenv("GARAGE_DRAIN_INTERVAL_DAYS", "30"))
WATER_FILTER_INTERVAL_DAYS = int(os.getenv("WATER_FILTER_INTERVAL_DAYS", "180"))
FILTER_INITIAL_STOCK = int(os.getenv("FILTER_INITIAL_STOCK", "1"))

# ─── WIRING ──────────────────────────────────────────────────────────────────


def build_tasks(chat: TelegramChat, file: JsonFile, app_state: AppState) -> dict:
    return {
        TaskType.ADD_SALT: AddSaltTask(
            stock=app_state.stock,
            days_per_salt_bag=DAYS_PER_SALT_BAG,
            chat=chat,
            file=file,
            app_state=app_state,
            name=TaskType.ADD_SALT,
            description=i18n.t(f"tasks.{TaskType.ADD_SALT.value}.title"),
            interval=DAYS_PER_SALT_BAG,
            notification_resend_interval=24,
            next_due=datetime.now()
        ),
        # TaskType.CLEAN_GARAGE_DRAIN: GarageDrainTask(
        #     chat=chat,
        #     file=file,
        #     app_state=app_state,
        #     name=TaskType.CLEAN_GARAGE_DRAIN,
        #     description=i18n.t(f"tasks.{TaskType.CLEAN_GARAGE_DRAIN.value}.title"),
        #     interval=GARAGE_DRAIN_INTERVAL_DAYS,
        #     notification_resend_interval=NOTIFICATION_RESEND_INTERVAL_HOURS,
        # ),
        TaskType.LOW_SALT_STOCK: LowSaltStockTask(
            stock=app_state.stock,
            chat=chat,
            file=file,
            app_state=app_state,
            name=TaskType.LOW_SALT_STOCK,
            description=i18n.t(f"tasks.{TaskType.LOW_SALT_STOCK.value}.title"),
            interval=0,
            notification_resend_interval=168,
        ),
        TaskType.CHANGE_WATER_FILTER: ChangeWaterFilterTask(
            stock=app_state.stock,
            chat=chat,
            file=file,
            app_state=app_state,
            name=TaskType.CHANGE_WATER_FILTER,
            description=i18n.t(f"tasks.{TaskType.CHANGE_WATER_FILTER.value}.title"),
            interval=WATER_FILTER_INTERVAL_DAYS,
            notification_resend_interval=168,
        ),
    }


def build_scheduler(bot, app_state, file) -> Scheduler:
    is_first_run = not Path(STATE_FILE).exists()

    if is_first_run:
        app_state.stock.salt_bags = SALT_INITIAL_STOCK
        app_state.stock.low_stock_threshold = SALT_LOW_STOCK_THRESHOLD
        app_state.stock.filters = FILTER_INITIAL_STOCK

    chat = TelegramChat(bot, GROUP_CHAT_ID)
    tasks = build_tasks(chat, file, app_state)

    for task_type, task in tasks.items():
        task.restore_from_dict(app_state.task_states.get(task_type.name, {}))

    return Scheduler(
        tasks=tasks,
        commands=[StartCommand(), DoneCommand(), StatusCommand(), RemindCommand(), GetStock()],
        chat=chat,
        admin_user_id=ADMIN_USER_ID,
        check_interval=SCHEDULER_CHECK_INTERVAL,
    )


def make_handler(command, scheduler, app_state):
    async def handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        await command.handle(update, ctx, scheduler, app_state)

    return handler


async def post_init(app: Application) -> None:
    scheduler = app.bot_data["scheduler"]
    await app.bot.set_my_commands([cmd.to_bot_command() for cmd in scheduler.commands])
    asyncio.create_task(scheduler.start())


# ─── MAIN ────────────────────────────────────────────────────────────────────


def main():
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO,
    )

    i18n.load()

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    file = JsonFile(STATE_FILE)
    app_state = file.load()

    scheduler = build_scheduler(app.bot, app_state, file)
    app.bot_data["scheduler"] = scheduler

    router = CallbackRouter(scheduler.tasks)

    commands = [StartCommand(), DoneCommand(), StatusCommand(), RemindCommand(), GetStock()]
    for command in commands:
        app.add_handler(CommandHandler(command.name, make_handler(command, scheduler, app_state)))

    app.add_handler(CallbackQueryHandler(router.handle))

    logging.info("Bot running...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
