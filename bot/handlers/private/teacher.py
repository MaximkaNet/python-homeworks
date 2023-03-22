from aiogram import Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher import FSMContext
from aiogram.utils.callback_data import CallbackData

from bot import models
from bot.utils import convert_week
from bot.utils.messages import TEACHER_PANEL_WELLCOME, TCH_PANEL_COMMANDS, ACTION_CANCELED, TEACHER_ADDED, TEACHER_EDITED, TEACHER_PANEL_BYE
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

    for item in teachers:
        act_kb = InlineKeyboardMarkup(row_width=2)
        act_kb.row()
        act_kb.insert(InlineKeyboardButton(
            "Edit", callback_data=show_teacher_actions.new("EDIT", item.name, json.dumps(item.work_days))))
        act_kb.insert(InlineKeyboardButton(
            "Delete", callback_data=show_teacher_actions.new("DELETE", item.name, "[]")))
        await message.answer(item.print(), reply_markup=act_kb)


async def __process_show(query: types.CallbackQuery, data: CallbackData, state: FSMContext):
    if data["act"] == "EDIT":
        async with state.proxy() as proxy_data:
            proxy_data["name"] = data["name"]
        _teacher = data["name"]
        work_days = json.loads(data["work_days"])
        await query.message.edit_text(f"Selected teacher: {_teacher}\nNow choose working day(s), where the teacher works.\n_Selected days: _" + ", ".join(map(str, convert_week(work_days))), reply_markup=await SelectWeekDays().start())
    elif data["act"] == "DELETE":
        delete_teacher = models.utils.teacher.convert_to_list(
            select.teacher_by(data["name"]))
        if not len(delete_teacher):
            # utils.debug(actions_show, "Obj not found.")
            await query.message.delete()
            await state.finish()
            await Teacher.workspace.set()
            return
        delete.teacher(data["name"])
        await query.message.delete()


async def __process_actions_show(query: types.CallbackQuery, data: CallbackData, state: FSMContext):
    selected, days = await SelectWeekDays().process_select(query, data)
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
            await query.message.edit_text(_teacher[0].print(), reply_markup=act_kb)


async def __add(message: types.Message):
    await message.answer("Type the teacher name:")
    await Teacher.name.set()


async def __name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
        await Teacher.work_days.set()
        await message.answer("Now choose working day(s), where the teacher works.", reply_markup=await SelectWeekDays([]).start())


async def __process_select_days(query: types.CallbackQuery, data: CallbackData, state: FSMContext):
    selected, days = await SelectWeekDays().process_select(query, data)
    if selected:
        if not len(days):
            await query.message.edit_text(ACTION_CANCELED)
        else:
            async with state.proxy() as proxy_data:
                name = proxy_data["name"]
                insert.teacher(name, days)
                await query.message.answer(TEACHER_ADDED)
        await state.finish()
        await Teacher.workspace.set()


async def __change_name(message: types.Message):
    tch_table = models.utils.teacher.gen_table()
    await message.answer("Select a teacher:", reply_markup=tch_table)


async def __process_select_change(query: types.CallbackQuery, data: CallbackData, state: FSMContext):
    teacher_name = data["name"]
    await query.message.edit_text(f"Selected teacher: *{teacher_name}*\nType new name.", )
    async with state.proxy() as proxy_data:
        proxy_data["name"] = data["name"]
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
    dp.register_message_handler(__teacher, commands=['teacher'])

    # show panel commands
    dp.register_message_handler(
        __help, commands=['help'], state=Teacher.workspace)

    # show all teachers
    dp.register_message_handler(
        __show, commands=["show"], state=Teacher.workspace)

    # add new teacher
    dp.register_message_handler(
        __add, commands=['add'], state=Teacher.workspace)

    # type teacher name
    dp.register_message_handler(__name, state=Teacher.name)

    # select a teacher
    dp.register_message_handler(__change_name, commands=[
                                'changename'], state=Teacher.workspace)

    # set new name
    dp.register_message_handler(__new_name, state=Teacher.new_name)

    # close workspace
    dp.register_message_handler(
        __close, commands=["close"], state=Teacher.workspace)

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
