import logging

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class CallbackRouter:
    def __init__(self, tasks: dict):
        self._callbacks = {
            key: (task, handler)
            for task in tasks.values()
            for key, handler in task.get_callbacks().items()
        }

    async def handle(self, update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
        query = update.callback_query
        await query.answer()

        user_name = query.from_user.full_name or str(query.from_user.id)
        parts = query.data.split(":")
        action = parts[0]
        route_key = f"{action}:{parts[1]}" if action == "done" else action
        value = None if action == "done" else int(parts[1])

        entry = self._callbacks.get(route_key)
        if not entry:
            return

        task, handler = entry
        if not task.pending:
            task.mark_pending()

        options = await handler(query, user_name, value)
        if options is not None:
            response = await task.complete_task(user_name, options)
            await query.edit_message_text(f"✓ {response}", parse_mode="HTML")
            logger.info(f"Task {task.name.name} completed by {user_name} via button.")
