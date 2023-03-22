
from aiogram import Dispatcher

from bot.handlers.private import register_private_handlers
from bot.handlers.group import register_group_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_private_handlers,
        register_group_handlers
    )
    for handler in handlers:
        handler(dp)
