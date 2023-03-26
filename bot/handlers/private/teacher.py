from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from bot import models
from bot.utils import convert_week
from bot.filters import IsPrivate
from bot.utils.messages import TEACHER_PANEL_WELLCOME, TCH_PANEL_COMMANDS, ACTION_CANCELED, TEACHER_ADDED, TEACHER_EDITED, TEACHER_PANEL_BYE, TEACHERS_NOT_FOUND
from bot.states.teacher import Teacher
from bot.database.methods import select, delete, update, insert
from bot.callbacks.teacher import show_teacher_actions, choice_teacher_callback
from bot.helpers.selectweekdays import SelectWeekDays
from bot.callbacks.selectweekdays import week_days_callback

import json


async def __teacher(message: types.Message):
    await Teacher.workspace.set()
    await message.answer(f"{TEACHER_PANEL_WELLCOME}\n\n{TCH_PANEL_COMMANDS}")


async def __help(message: types.Message):
    await message.answer(TCH_PANEL_COMMANDS)


async def __show(message: types.Message):
    teachers = models.utils.teacher.convert_to_list(select.teachers())
    if len(teachers) == 0:
        await message.answer(TEACHERS_NOT_FOUND)
        return
    for item in teachers:
        act_kb = InlineKeyboardMarkup(row_width=2)
        act_kb.row()
        act_kb.insert(InlineKeyboardButton(
            "Edit", callback_data=show_teacher_actions.new("EDIT", item.name, json.dumps(item.work_days))))
        act_kb.insert(InlineKeyboardButton(
            "Delete", callback_data=show_teacher_actions.new("DELETE", item.name, "[]")))
        await message.answer(item.print(), reply_markup=act_kb)


async def __process_show(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    if callback_data["act"] == "EDIT":
        async with state.proxy() as proxy_data:
            proxy_data["name"] = callback_data["name"]
        _teacher = callback_data["name"]
        work_days = json.loads(callback_data["work_days"])
        await callback_query.message.edit_text(f"Selected teacher: {_teacher}\nNow choose working day(s), where the teacher works.\n_Selected days: _" + ", ".join(map(str, convert_week(work_days))), reply_markup=await SelectWeekDays().start(work_days))
    elif callback_data["act"] == "DELETE":
        delete_teacher = models.utils.teacher.convert_to_list(
            select.teacher_by(callback_data["name"]))
        if not len(delete_teacher):
            # utils.debug(actions_show, "Obj not found.")
            await callback_query.message.delete()
            await state.finish()
            await Teacher.workspace.set()
            return
        delete.teacher(callback_data["name"])
        await callback_query.message.delete()


async def __process_actions_show(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, days = await SelectWeekDays().process_select(callback_query, callback_data)
    if selected:
        async with state.proxy() as proxy_data:
            update.teacher(proxy_data["name"], days)
        act_kb = InlineKeyboardMarkup(row_width=2)
        act_kb.row()
        act_kb.insert(InlineKeyboardButton(
            "Edit", callback_data=show_teacher_actions.new("EDIT", proxy_data["name"], days)))
        act_kb.insert(InlineKeyboardButton(
            "Delete", callback_data=show_teacher_actions.new("DELETE", proxy_data["name"], [])))
        _teacher = models.utils.teacher.convert_to_list(
            select.teacher_by(proxy_data["name"]))
        if len(_teacher):
            await callback_query.message.edit_text(_teacher[0].print(), reply_markup=act_kb)


async def __add(message: types.Message):
    await message.answer("Type the teacher name:")
    await Teacher.name.set()


async def __name(message: types.Message, state: FSMContext):
    # check unique name
    if len(select.teacher_by(message.text)) != 0:
        await message.answer("Already exist. /help")
        await state.finish()
        await Teacher.workspace.set()
        return
    async with state.proxy() as data:
        data["name"] = message.text
        await Teacher.work_days.set()
        await message.answer("Now choose working day(s), where the teacher works.", reply_markup=await SelectWeekDays().start())


async def __process_select_days(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, days = await SelectWeekDays().process_select(callback_query, callback_data)
    if selected:
        if not len(days):
            await callback_query.message.edit_text(ACTION_CANCELED)
        else:
            async with state.proxy() as proxy_data:
                name = proxy_data["name"]
                insert.teacher(name, days)
                await callback_query.message.answer(TEACHER_ADDED)
        await state.finish()
        await Teacher.workspace.set()


async def __change_name(message: types.Message):
    tch_table = models.utils.teacher.gen_table()
    if tch_table == None:
        await message.answer(TEACHERS_NOT_FOUND)
        return
    await message.answer("Select a teacher:", reply_markup=tch_table)


async def __process_select_change(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    teacher_name = callback_data["name"]
    await callback_query.message.edit_text(f"Selected teacher: *{teacher_name}*\nType new name.", )
    async with state.proxy() as proxy_data:
        proxy_data["name"] = callback_data["name"]
    await Teacher.new_name.set()


async def __new_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        update.teacher(data["name"], new_name=message.text)
    await state.finish()
    await Teacher.workspace.set()
    await message.answer(TEACHER_EDITED)


async def __close(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(TEACHER_PANEL_BYE)


def register_teacher_handlers(dp: Dispatcher):
    # select teacher panel
    dp.register_message_handler(
        __teacher, IsPrivate(), commands=['teacher'], state="*")

    # show panel commands
    dp.register_message_handler(
        __help, IsPrivate(), commands=['help'], state=Teacher.workspace)

    # show all teachers
    dp.register_message_handler(
        __show, IsPrivate(), commands=["show"], state=Teacher.workspace)

    # add new teacher
    dp.register_message_handler(
        __add, IsPrivate(), commands=['add'], state=Teacher.workspace)

    # type teacher name
    dp.register_message_handler(__name, state=Teacher.name)

    # select a teacher
    dp.register_message_handler(__change_name, IsPrivate(), commands=[
                                'changename'], state=Teacher.workspace)

    # set new name
    dp.register_message_handler(__new_name, state=Teacher.new_name)

    # close workspace
    dp.register_message_handler(
        __close, IsPrivate(), commands=["close"], state=Teacher.workspace)

    # show actions
    dp.register_callback_query_handler(
        __process_show, show_teacher_actions.filter(), state=Teacher.workspace)

    # handle show actions
    dp.register_callback_query_handler(
        __process_actions_show, week_days_callback.filter(), state=Teacher.workspace)

    # select days for a teacher
    dp.register_callback_query_handler(
        __process_select_days, week_days_callback.filter(), state=Teacher.work_days)

    # select teacher for change name
    dp.register_callback_query_handler(
        __process_select_change, choice_teacher_callback.filter(), state=Teacher.workspace)
