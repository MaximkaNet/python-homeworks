import logging

from bot.utils.env import Config
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.handlers.main import register_all_handlers


async def _on_startup(dp: Dispatcher):
    logging.debug("Bot started.")
    register_all_handlers(dp)


def start_bot() -> None:
    bot = Bot(token=Config.TOKEN, proxy=Config.PROXY, parse_mode="markdown")
    dp = Dispatcher(bot, storage=MemoryStorage())
    executor.start_polling(dp, skip_updates=True, on_startup=_on_startup)
