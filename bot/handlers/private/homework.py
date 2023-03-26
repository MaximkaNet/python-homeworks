from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils.messages import HOMEWORKS_NOT_FOUND, HELP_ADD, HOMEWORK_PANEL_WELLCOME, HW_PANEL_COMMANDS, SELECT_TEACHER, TEACHERS_NOT_FOUND, HOMEWORK_PANEL_BYE, ADD_TASK, ACTION_CANCELED, HOMEWORK_EDITED, INCORRECT, HOMEWORK_UPDATE_QUESTION, HOMEWORK_ADDED, HOMEWORK_DELETED
from bot.callbacks.homework import show_homework_callback, actions_show_all_callback
from bot.callbacks.teacher import choice_teacher_callback
from bot.states.homowerk import Homework
from bot.utils.env import Config
from bot.filters import IsPrivate
from bot import models

from bot.database.methods import select, delete

from aiogram_calendar import dialog_cal_callback, DialogCalendar

from datetime import date, timedelta, datetime


async def __add_help(msg: types.Message) -> None:
    await msg.answer(HELP_ADD)


async def __homework(msg: types.Message) -> None:
    await Homework.workspace.set()
    await msg.answer(f"{HOMEWORK_PANEL_WELLCOME}\n\n{HW_PANEL_COMMANDS}")


async def __help(msg: types.Message) -> None:
    await msg.answer(HW_PANEL_COMMANDS)


async def __show(msg: types.Message) -> None:
    await Homework.show.set()
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton("Tomorrow", callback_data=show_homework_callback.new("tomorrow", "private")),
            InlineKeyboardButton("Another", callback_data=show_homework_callback.new("another", "private")))
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
            await Homework.workspace.set()
            return
        # print results
        wrapper = f"{show_list[0].print()}\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(wrapper,
                                               reply_markup=None)
        for show_item in range(1, len(show_list)):
            wrapper = f"{show_item.print()}\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
            await callback_query.message.answer(wrapper)
        await state.finish()
        await Homework.workspace.set()
    elif callback_data["act"] == "another":
        await callback_query.message.edit_reply_markup(await DialogCalendar().start_calendar())
        await state.finish()
        await Homework.workspace.set()


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


async def __add(msg: types.Message, state: FSMContext) -> None:
    await Homework.teacher.set()
    tch_table = models.utils.teacher.gen_table()
    if tch_table != None:
        await msg.answer(SELECT_TEACHER, reply_markup=tch_table)
        return
    await msg.answer(TEACHERS_NOT_FOUND)
    await state.finish()
    await Homework.workspace.set()


async def __process_teacher(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    async with state.proxy() as proxy_data:
        proxy_data["teacher"] = callback_data["name"]
        proxy_data["add_date"] = date.today()
        selected_teacher = f"{SELECT_TEACHER} _{proxy_data['teacher']}_"
        await callback_query.message.edit_text(selected_teacher)
        # check existed homework
        is_exist = models.utils.homework.get_by(
            proxy_data["teacher"], proxy_data["add_date"])
        if is_exist:
            proxy_data["homework"] = is_exist
            await Homework.edit_question.set()
            await callback_query.message.edit_text(
                f"{selected_teacher}\n\n{HOMEWORK_UPDATE_QUESTION}")
            return
        await callback_query.message.edit_text(f"{selected_teacher}\n{ADD_TASK}")
        await Homework.work.set()


async def __edit_homework_question(msg: types.Message, state: FSMContext) -> None:
    if msg.text.lower() == "yes":
        async with state.proxy() as proxy_data:
            homework: models.Homework = proxy_data["homework"]
            selected_teacher = f"{SELECT_TEACHER} _{proxy_data['teacher']}_"
            if homework:
                await msg.answer(f"{selected_teacher}\n{ADD_TASK}")
                await msg.answer(homework.convert_tasks())
                await Homework.edit.set()
    else:
        await msg.answer(ACTION_CANCELED)
        await state.finish()
        await Homework.workspace.set()


async def __edit_homework(msg: types.Message, state: FSMContext) -> None:
    if msg.text == "/cancel":
        await msg.answer(ACTION_CANCELED)
        await state.finish()
        await Homework.workspace.set()
        return
    elif msg.text == "/hadd":
        await msg.answer(HELP_ADD)
        return
    temp_homework = models.Homework()
    isValid = temp_homework.parse_message(msg.text)
    if isValid:
        async with state.proxy() as proxy_data:
            homework: models.Homework = proxy_data["homework"]
            homework.update(temp_homework.tasks)
            # utils.log(edit_homework, "Update homework",
            #           user=f"{message.from_user.full_name} ({message.from_user.username})")
            await msg.answer(HOMEWORK_EDITED)
            await state.finish()
            await Homework.workspace.set()
            return
    else:
        await msg.answer(INCORRECT)
        await msg.answer(ADD_TASK)
        return


async def __get_work(msg: types.Message, state: FSMContext) -> None:
    if msg.text == "/hadd":
        await msg.answer(HELP_ADD)
        return
    if msg.text == "/cancel":
        await msg.answer(ACTION_CANCELED)
        await state.finish()
        await Homework.workspace.set()
        return
    async with state.proxy()as proxy_data:
        temp_obj = models.Homework()
        isValid = temp_obj.parse_message(msg.text)
        if isValid:
            temp_obj.create(proxy_data["teacher"])
            await msg.answer(HOMEWORK_ADDED)
            # utils.log(process_work, "Create homework",
            #           user=f"{msg.from_user.full_name} ({msg.from_user.username})")
            await state.finish()
            await Homework.workspace.set()
        else:
            await msg.answer(INCORRECT)
            await msg.answer(ADD_TASK)
            await Homework.work.set()


async def __show_last(msg: types.Message, regexp_command, state: FSMContext) -> None:
    count_hw = int(regexp_command.group(1)) if regexp_command.group(
        1) and int(regexp_command.group(1)) > 0 else 2
    tch_table = models.utils.teacher.gen_table()
    if tch_table == None:
        await msg.answer(TEACHERS_NOT_FOUND)
        return
    await Homework.show_last.set()
    async with state.proxy() as proxy_data:
        proxy_data["show_last"] = count_hw
    await msg.answer(SELECT_TEACHER, reply_markup=tch_table)


async def __process_teacher_show_last(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    _count_hw: int = 2
    async with state.proxy() as proxy_data:
        _count_hw = proxy_data["show_last"]
    _teacher: str = callback_data["name"]
    _homeworks: list[models.Homework] = models.utils.homework.convert_to_list(
        select.homeworks(limit=_count_hw, author=_teacher))
    if len(_homeworks) == 0:
        await callback_query.message.edit_text(HOMEWORKS_NOT_FOUND)
        await state.finish()
        await Homework.workspace.set()
        return
    for i, item in enumerate(_homeworks):
        actions = InlineKeyboardMarkup()
        callback_edit = actions_show_all_callback.new(
            "EDIT", f"{item.author}", f"{item.date.strftime(Config.DATE_FORMAT)}")
        callback_delete = actions_show_all_callback.new(
            "DELETE", f"{item.author}", f"{item.date.strftime(Config.DATE_FORMAT)}")
        edit = InlineKeyboardButton(
            "Edit", callback_data=callback_edit)
        delete = InlineKeyboardButton(
            "Delete", callback_data=callback_delete)
        actions.add(edit, delete)
        if i == 0:
            await callback_query.message.edit_text(item.print(), reply_markup=actions)
            continue
        await callback_query.message.answer(item.print(), reply_markup=actions)
    await state.finish()
    await Homework.workspace.set()


async def __process_actions_show_last(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    if (callback_data["action"] == "EDIT"):
        async with state.proxy() as proxy_data:
            date = datetime.strptime(
                callback_data["date"], Config.DATE_FORMAT).date()
            _homework: models.Homework = models.utils.homework.get_by(
                callback_data["author"], date)
            proxy_data["homework"] = _homework
            selected_teacher = f"{SELECT_TEACHER} _{callback_data['author']}_"
            if _homework:
                await callback_query.message.answer(f"{selected_teacher}\n{ADD_TASK}")
                await callback_query.message.answer(_homework.convert_tasks())
                await Homework.edit.set()
    else:
        date = datetime.strptime(
            callback_data["date"], Config.DATE_FORMAT).date()
        delete_homework = models.utils.homework.get_by(
            callback_data["author"], date)
        if not delete_homework:
            # utils.debug(process_homeworks_actions, "Obj not found.")
            await callback_query.message.delete()
            await state.finish()
            await Homework.workspace.set()
            return
        delete.homework(date, callback_data["author"])
        await callback_query.message.edit_text(HOMEWORK_DELETED)
        await state.finish()
        await Homework.workspace.set()


async def __close(msg: types.Message, state: FSMContext) -> None:
    await msg.answer(HOMEWORK_PANEL_BYE)
    await state.finish()


def register_homework_handlers(dp: Dispatcher) -> None:
    # add action help
    dp.register_message_handler(
        __add_help, IsPrivate(), commands=['addh'], state="*")

    # switch to homework panel
    dp.register_message_handler(
        __homework, IsPrivate(), commands=['homework'], state="*")

    # commands in panel
    dp.register_message_handler(
        __help, IsPrivate(), commands=['help'], state=Homework.workspace)

    # show homework
    dp.register_message_handler(
        __show, IsPrivate(), commands=['show'], state=Homework.workspace)

    # add homework
    dp.register_message_handler(
        __add, IsPrivate(), commands=['add'], state=Homework.workspace)

    # get message with excersices
    dp.register_message_handler(__get_work, state=Homework.work)
    # show several homeworks
    dp.register_message_handler(__show_last, filters.RegexpCommandsFilter(
        regexp_commands=['showlast([0-9]*)']), state=Homework.workspace)

    # close homework panel
    dp.register_message_handler(
        __close, IsPrivate(), commands=['close'], state=Homework.workspace)

    # edit question
    dp.register_message_handler(
        __edit_homework_question, state=Homework.edit_question)

    # edit homework
    dp.register_message_handler(__edit_homework, state=Homework.edit)

    # callback handlers

    dp.register_callback_query_handler(
        __process_show, show_homework_callback.filter(), state=Homework.show)

    # show calendar
    dp.register_callback_query_handler(
        __process_calendar, dialog_cal_callback.filter(), state="*")

    # selecting teacher for adding homework
    dp.register_callback_query_handler(
        __process_teacher, choice_teacher_callback.filter(), state=Homework.teacher)

    # select teacher for showing homeworks
    dp.register_callback_query_handler(
        __process_teacher_show_last, choice_teacher_callback.filter(), state=Homework.show_last)

    # show list actions
    dp.register_callback_query_handler(
        __process_actions_show_last, actions_show_all_callback.filter(), state=Homework.workspace)
