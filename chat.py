from abc import ABC, abstractmethod

import i18n
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
            InlineKeyboardButton(i18n.t("buttons.done"), callback_data=callback_data),
        ]])

    @staticmethod
    def bags_keyboard() -> InlineKeyboardMarkup:
        counts = [1, 2, 3, 4, 5, 6]
        buttons = [
            InlineKeyboardButton(i18n.t(f"buttons.bags.{n}"), callback_data=f"bags:{n}")
            for n in counts
        ]
        return InlineKeyboardMarkup([buttons[:3], buttons[3:]])

    @staticmethod
    def order_keyboard() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("4",  callback_data="order:4"),
            InlineKeyboardButton("5",  callback_data="order:5"),
            InlineKeyboardButton("6",  callback_data="order:6"),
            InlineKeyboardButton("7",  callback_data="order:7"),
            InlineKeyboardButton("8",  callback_data="order:8"),
            InlineKeyboardButton("9",  callback_data="order:9"),
            InlineKeyboardButton("10", callback_data="order:10"),
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
