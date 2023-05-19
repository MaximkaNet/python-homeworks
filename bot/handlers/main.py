from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.storage import FSMContext

from ..utils.messages import WELLCOME, HELP, ABOUT, HELP_ADMIN
from ..filters import IsPrivate, IsPublic


async def __start(msg: Message, state: FSMContext):
    await msg.answer(WELLCOME)


async def __help(msg: Message, state: FSMContext):
    await msg.answer(HELP)


async def __help_admin(msg: Message, state: FSMContext):
    await msg.answer(HELP_ADMIN)


async def __about(msg: Message, state: FSMContext):
    await msg.answer(ABOUT)


def register_main_handlers(dp: Dispatcher):
    dp.register_message_handler(
        __start, commands=['start'], state="*")
    dp.register_message_handler(
        __help, IsPublic(), commands=['help'], state="*")
    dp.register_message_handler(
        __help_admin, IsPrivate(), commands=['help'], state="*")
    dp.register_message_handler(
        __about, commands=['about'], state="*")
