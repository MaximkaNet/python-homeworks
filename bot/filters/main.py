from aiogram import types
from aiogram.dispatcher.filters import Filter


class IsPrivate(Filter):
    key = "is_private"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "private" else False


class IsGroup(Filter):
    key = "is_group"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "group" else False


class IsSupergroup(Filter):
    key = "is_supergroup"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "supergroup" else False


class IsChannel(Filter):
    key = "is_channel"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "channel" else False
