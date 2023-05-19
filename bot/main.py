import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config.bot import BotConfig
from .handlers import register_all_handlers


async def __on_startup(dp: Dispatcher) -> None:
    logging.info("Admin bot started.")
    register_all_handlers(dp)


def start_bot() -> None:
    try:
        bot = Bot(token=BotConfig.TOKEN,
                  proxy=None if BotConfig.PROXY == "None" else BotConfig.PROXY,
                  parse_mode="markdown")
        dp = Dispatcher(bot, storage=MemoryStorage())
        executor.start_polling(dp, skip_updates=True, on_startup=__on_startup)
    except Exception as err:
        print(err)
