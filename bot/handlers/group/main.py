from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils.messages import WELLCOME_GROUP, HOMEWORKS_NOT_FOUND, SERVICE_UNAVAILABLE
from bot.callbacks.homework import show_homework_callback
from bot.states.homowerk import Homework
from bot.utils.env import Config
from bot.filters import IsGroup, IsSupergroup
from bot import models
from bot.middlewares import check_connection

from aiogram_calendar import dialog_cal_callback, DialogCalendar

from datetime import date, timedelta


async def __start(msg: types.Message) -> None:
    await msg.answer(WELLCOME_GROUP)


async def __help(msg: types.Message) -> None:
    await msg.answer(WELLCOME_GROUP)


async def __homework(msg: types.Message) -> None:
    # database availability check
    if not check_connection():
        await msg.answer(SERVICE_UNAVAILABLE)
        return
    await Homework.show.set()
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton("Tomorrow", callback_data=show_homework_callback.new("tomorrow", "group")),
            InlineKeyboardButton("Another", callback_data=show_homework_callback.new("another", "group")))
    await msg.reply("Select a date:", reply_markup=ikb)


async def __process_show(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    if callback_data["act"] == "tomorrow":
        selected_date: date = date.today() + timedelta(days=1)
        # loading..
        wrapper = f"*Loading...*\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
        # find homeworks
        show_list: list[models.Homework] = models.utils.homework.get_last_by_date(
            selected_date)
        await callback_query.message.edit_text(
            wrapper, reply_markup=None)
        if len(show_list) == 0:
            wrapper = f"*{HOMEWORKS_NOT_FOUND}*\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
            await callback_query.message.edit_text(wrapper, reply_markup=None)
            await state.finish()
            return
        # print results
        wrapper = f"{show_list[0].print()}\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(wrapper,
                                               reply_markup=None)
        for show_item in range(1, len(show_list)):
            wrapper = f"{show_item.print()}\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
            await callback_query.message.answer(wrapper)
        await state.finish()
    elif callback_data["act"] == "another":
        await callback_query.message.edit_reply_markup(await DialogCalendar().start_calendar())
        await state.finish()


async def __process_calendar(callback_query: types.CallbackQuery, callback_data: CallbackData) -> None:
    _selected, _date = await DialogCalendar().process_selection(callback_query, callback_data)
    if _selected:
        selected_date: date = _date.date()
        # find homeworks
        show_list: list[models.Homework] = models.utils.homework.get_last_by_date(
            selected_date)
        # loading..
        wrapper = f"*Loading...*\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(
            wrapper, reply_markup=None)
        if len(show_list) == 0:
            wrapper = f"*{HOMEWORKS_NOT_FOUND}*\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
            await callback_query.message.edit_text(wrapper, reply_markup=None)
            return
        # print results
        wrapper = f"{show_list[0].print()}\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(wrapper,
                                               reply_markup=None)
        for show_item in range(1, len(show_list)):
            wrapper = f"{show_item.print()}\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
            await callback_query.message.answer(wrapper)


def register_group_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        __start, IsGroup() | IsSupergroup(), commands=['start'], state="*")
    dp.register_message_handler(
        __help, IsGroup() | IsSupergroup(), commands=['help'], state="*")
    dp.register_message_handler(
        __homework, IsGroup() | IsSupergroup(), commands=['homework'], state="*")

    dp.register_callback_query_handler(
        __process_show, show_homework_callback.filter(), state=Homework.show)
    dp.register_callback_query_handler(
        __process_calendar, dialog_cal_callback.filter(), state="*")
