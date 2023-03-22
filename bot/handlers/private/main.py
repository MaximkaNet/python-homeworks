from aiogram import types
from aiogram.dispatcher import Dispatcher

from bot.utils.messages import WELLCOME_USER

from bot.handlers.private.homework import register_homework_handlers
from bot.handlers.private.teacher import register_teacher_handlers


async def __start(msg: types.Message):
    await msg.answer(WELLCOME_USER)


async def __help(msg: types.Message):
    await msg.answer(WELLCOME_USER)


def register_private_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(__start, commands=['start'])
    dp.register_message_handler(__help, commands=['help'])

    handlers = (
        register_homework_handlers,
        register_teacher_handlers
    )
    for handler in handlers:
        handler(dp)
