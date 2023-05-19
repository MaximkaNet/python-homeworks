from aiogram import types
from aiogram.dispatcher.filters import Filter


class IsPrivate(Filter):
    key = "is_private"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "private" else False
