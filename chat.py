from abc import ABC, abstractmethod

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Chat(ABC):

    @staticmethod
    def tasks_keyboard(tasks: list) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(task.description, callback_data=f"done:{task.name.name}")]
            for task in tasks
        ])

    @staticmethod
    def done_keyboard(callback_data: str) -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("Zavrseno ✓", callback_data=callback_data),
        ]])

    @staticmethod
    def bags_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1 kesa", callback_data="bags:1"),
                InlineKeyboardButton("2 kese", callback_data="bags:2"),
                InlineKeyboardButton("3 kese", callback_data="bags:3"),
            ],
            [
                InlineKeyboardButton("4 kese", callback_data="bags:4"),
                InlineKeyboardButton("5 kesa", callback_data="bags:5"),
                InlineKeyboardButton("6 kesa", callback_data="bags:6"),
            ],
        ])

    @staticmethod
    def order_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("5",  callback_data="order:5"),
            InlineKeyboardButton("10", callback_data="order:10"),
            InlineKeyboardButton("15", callback_data="order:15"),
            InlineKeyboardButton("20", callback_data="order:20"),
        ]])

    @abstractmethod
    async def send(self, message: str, reply_markup=None) -> None:
        raise NotImplementedError

    @abstractmethod
    async def send_to_user(self, user_id: int, message: str) -> None:
        raise NotImplementedError


class TelegramChat(Chat):
    def __init__(self, bot, group_chat_id: int):
        self._bot = bot
        self._group_chat_id = group_chat_id

    async def send(self, message: str, reply_markup=None) -> None:
        await self._bot.send_message(
            chat_id=self._group_chat_id,
            text=message,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )

    async def send_to_user(self, user_id: int, message: str) -> None:
        await self._bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode="HTML",
        )
