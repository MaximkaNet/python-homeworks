from aiogram import types
from aiogram.dispatcher.filters import Filter


class IsPublic(Filter):
    key = "is_public"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "group" or message.chat.type == "supergroup" else False
