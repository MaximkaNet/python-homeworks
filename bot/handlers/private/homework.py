from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher import FSMContext, filters
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.utils.messages import HOMEWORKS_NOT_FOUND, HELP_ADD, HOMEWORK_PANEL_WELLCOME, HW_PANEL_COMMANDS, SELECT_TEACHER, TEACHERS_NOT_FOUND, HOMEWORK_PANEL_BYE, ADD_TASK, ACTION_CANCELED, HOMEWORK_EDITED, INCORRECT, HOMEWORK_UPDATE_QUESTION, HOMEWORK_ADDED, SERVICE_UNAVAILABLE, ADD_ATTACHMENTS
from bot.callbacks.homework import show_homework_callback, actions_show_all_callback
from bot.callbacks.teacher import choice_teacher_callback
from bot.states.homowerk import Homework
from bot.utils.env import Config
from bot.filters import IsPrivate
from bot import models
from bot.middlewares import check_connection
from bot.utils import log
from bot.models.utils.homework import save_file

from bot.database.methods import select, delete

from aiogram_calendar import dialog_cal_callback, DialogCalendar

from datetime import date, timedelta, datetime


async def __add_help(msg: types.Message) -> None:
    await msg.answer(HELP_ADD)


async def __homework(msg: types.Message) -> None:
    await Homework.workspace.set()
    await msg.answer(f"{HOMEWORK_PANEL_WELLCOME}\n\n{HW_PANEL_COMMANDS}")
    log("Open homework panel", msg.from_user.full_name)


async def __help(msg: types.Message) -> None:
    await msg.answer(HW_PANEL_COMMANDS)


async def __show(msg: types.Message) -> None:
    await Homework.show.set()
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton("Tomorrow", callback_data=show_homework_callback.new("tomorrow", "private")),
            InlineKeyboardButton("Another", callback_data=show_homework_callback.new("another", "private")))
    await msg.reply("Select a date:", reply_markup=ikb)


async def __process_show(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    log("Get homework", callback_query.from_user.full_name)
    if callback_data["act"] == "tomorrow":
        # database availability check
        if not check_connection():
            await callback_query.message.answer(SERVICE_UNAVAILABLE)
            await Homework.workspace.set()
            return

        selected_date: date = date.today() + timedelta(days=1)
        # loading..
        wrapper = f"*Loading...*\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
        # find homeworks
        await callback_query.message.edit_text(
            wrapper, reply_markup=None)
        show_list: list[models.Homework] = models.utils.homework.get_last_by_date(
            selected_date)
        if len(show_list) == 0:
            wrapper = f"*{HOMEWORKS_NOT_FOUND}*\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
            await callback_query.message.edit_text(wrapper, reply_markup=None)
            await Homework.workspace.set()
            return
        # print results
        wrapper = f"{show_list[0].print()}\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(wrapper,
                                               reply_markup=None)
        # print attachments
        homework_id = select.homework_id(
            show_list[0].author, show_list[0].date)
        await __show_attachments(callback_query.message, homework_id)

        for show_item in range(1, len(show_list)):
            wrapper = f"{show_item.print()}\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
            await callback_query.message.answer(wrapper)
            # print attachments
            homework_id = select.homework_id(show_item.author, show_item.date)
            await __show_attachments(callback_query.message, homework_id)
        await Homework.workspace.set()
    elif callback_data["act"] == "another":
        await callback_query.message.edit_reply_markup(await DialogCalendar().start_calendar())
        await Homework.workspace.set()


async def __process_calendar(callback_query: types.CallbackQuery, callback_data: CallbackData) -> None:
    _selected, _date = await DialogCalendar().process_selection(callback_query, callback_data)
    if _selected:
        # database availability check
        if not check_connection():
            await callback_query.message.answer(SERVICE_UNAVAILABLE)
            return
        selected_date: date = _date.date()
        # loading..
        wrapper = f"*Loading...*\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(
            wrapper, reply_markup=None)
        # find homeworks
        show_list: list[models.Homework] = models.utils.homework.get_last_by_date(
            selected_date)
        if len(show_list) == 0:
            wrapper = f"*{HOMEWORKS_NOT_FOUND}*\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
            await callback_query.message.edit_text(wrapper, reply_markup=None)
            return
        # print results
        wrapper = f"{show_list[0].print()}\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(wrapper,
                                               reply_markup=None)
        # print attachments
        homework_id = select.homework_id(
            show_list[0].author, show_list[0].date)
        await __show_attachments(callback_query.message, homework_id)

        for show_item in range(1, len(show_list)):
            wrapper = f"{show_item.print()}\n_Selected date: {selected_date.strftime(Config.DATE_FORMAT)}_"
            await callback_query.message.answer(wrapper)
            # print attachments
            homework_id = select.homework_id(show_item.author, show_item.date)
            await __show_attachments(callback_query.message, homework_id)


async def __show_attachments(msg: types.Message, homework_id: int) -> None:
    photos, files, animations = models.utils.homework.get_files(homework_id)
    if len(photos) != 0:
        for item in photos:
            await msg.answer_photo(item)
    if len(files) != 0:
        for item in files:
            await msg.answer_document(item)
    if len(animations) != 0:
        for item in animations:
            await msg.answer_animation(item)


async def __add(msg: types.Message, state: FSMContext) -> None:
    # database availability check
    if not check_connection():
        await msg.answer(SERVICE_UNAVAILABLE)
        return
    await Homework.teacher.set()
    tch_table = models.utils.teacher.gen_table()
    if tch_table != None:
        await msg.answer(SELECT_TEACHER, reply_markup=tch_table)
        return
    await msg.answer(TEACHERS_NOT_FOUND)
    await Homework.workspace.set()


async def __process_teacher(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    # database availability check
    if not check_connection():
        await callback_query.message.answer(SERVICE_UNAVAILABLE)
        await Homework.workspace.set()
        return
    async with state.proxy() as proxy_data:
        proxy_data["teacher"] = callback_data["name"]
        proxy_data["added_date"] = date.today()
        SELECTED_TEACHER = f"{SELECT_TEACHER} _{proxy_data['teacher']}_"
        await callback_query.message.edit_text(SELECTED_TEACHER)
        # check existed homework
        is_exist = models.utils.homework.get_by(
            proxy_data["teacher"], proxy_data["added_date"])
        if is_exist:
            proxy_data["homework"] = is_exist
            await Homework.edit_question.set()
            await callback_query.message.edit_text(
                f"{SELECTED_TEACHER}\n\n{HOMEWORK_UPDATE_QUESTION}")
            return
        await callback_query.message.edit_text(f"{SELECTED_TEACHER}\n{ADD_TASK}")
        await Homework.work.set()


async def __edit_homework_question(msg: types.Message, state: FSMContext) -> None:
    if msg.text.lower() == "yes":
        async with state.proxy() as proxy_data:
            homework: models.Homework = proxy_data["homework"]
            SELECTED_TEACHER = f"{SELECT_TEACHER} _{proxy_data['teacher']}_"
            if homework:
                await msg.answer(f"{SELECTED_TEACHER}\n{ADD_TASK}")
                await msg.answer(homework.convert_tasks())
                await Homework.edit.set()
    else:
        await msg.answer(ACTION_CANCELED)
        await Homework.workspace.set()


async def __edit_homework(msg: types.Message, state: FSMContext) -> None:
    # database availability check
    if not check_connection():
        await msg.answer(SERVICE_UNAVAILABLE)
        await Homework.workspace.set()
        return
    if msg.text == "/cancel":
        await msg.answer(ACTION_CANCELED)
        await Homework.workspace.set()
        return
    elif msg.text == "/hadd":
        await msg.answer(HELP_ADD)
        return
    async with state.proxy() as proxy_data:
        temp_homework = models.Homework(
            proxy_data["added_date"],
            proxy_data["added_date"],
            proxy_data["teacher"])
        isValid = temp_homework.parse_message(msg.text)
        if isValid:
            temp_homework.update()
            await Homework.attachments.set()
            return
        else:
            await msg.answer(INCORRECT)
            await msg.answer(ADD_TASK)
            return


async def __get_work(msg: types.Message, state: FSMContext) -> None:
    # database availability check
    if not check_connection():
        await msg.answer(SERVICE_UNAVAILABLE)
        await Homework.workspace.set()
        return
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
            proxy_data["homework"] = temp_obj
            await msg.answer(ADD_ATTACHMENTS)
            await Homework.attachments.set()
        else:
            await msg.answer(INCORRECT)
            await msg.answer(ADD_TASK)
            await Homework.work.set()


async def __get_files(msg: types.Message, state: FSMContext) -> None:
    if msg.text == "/finish":  # check end of add files
        async with state.proxy() as proxy_data:
            await msg.answer(HOMEWORK_ADDED)
            log("Added new homework", msg.from_user.full_name)
            await state.finish()
            await Homework.workspace.set()
        return

    # find and save files
    async with state.proxy() as proxy_data:
        homework: models.Homework = proxy_data["homework"]
        await save_file(msg, homework)


async def __show_last(msg: types.Message, regexp_command, state: FSMContext) -> None:
    # database availability check
    if not check_connection():
        await msg.answer(SERVICE_UNAVAILABLE)
        return
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
    # database availability check
    if not check_connection():
        await callback_query.message.answer(SERVICE_UNAVAILABLE)
        await Homework.workspace.set()
        return
    _count_hw: int = 2
    async with state.proxy() as proxy_data:
        _count_hw = proxy_data["show_last"]
    _teacher: str = callback_data["name"]
    # loading...
    wrapper = f"*Loading...*\n_Selected teacher: {_teacher}_"
    await callback_query.message.edit_text(
        wrapper, reply_markup=None)
    # find homeworks
    _homeworks: list[models.Homework] = models.utils.homework.convert_to_list(
        select.homeworks(limit=_count_hw, author=_teacher))
    if len(_homeworks) == 0:
        await callback_query.message.edit_text(HOMEWORKS_NOT_FOUND)
        log(f"Show {_count_hw} homeworks",
            callback_query.from_user.full_name)
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
    log(f"Show {_count_hw} homeworks",
        callback_query.from_user.full_name)
    await Homework.workspace.set()


async def __process_actions_show_last(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext) -> None:
    # database availability check
    if not check_connection():
        await callback_query.message.answer(SERVICE_UNAVAILABLE)
        await Homework.workspace.set()
        return
    if (callback_data["action"] == "EDIT"):
        async with state.proxy() as proxy_data:
            date = datetime.strptime(
                callback_data["date"], Config.DATE_FORMAT).date()
            getted_homework: models.Homework = models.utils.homework.get_by(
                callback_data["author"], date)
            proxy_data["homework"] = getted_homework
            SELECTED_TEACHER = f"{SELECT_TEACHER} _{callback_data['author']}_"
            if getted_homework:
                await callback_query.message.answer(f"{SELECTED_TEACHER}\n{ADD_TASK}")
                await callback_query.message.answer(getted_homework.convert_tasks())
                await Homework.edit.set()
    else:
        date = datetime.strptime(
            callback_data["date"], Config.DATE_FORMAT).date()
        delete_homework = models.utils.homework.get_by(
            callback_data["author"], date)
        if not delete_homework:
            await callback_query.message.delete()
            await Homework.workspace.set()
            return
        delete.homework(date, callback_data["author"])
        log(f"Deleted homework", callback_query.from_user.full_name)
        await callback_query.message.delete()
        await Homework.workspace.set()


async def __add_empty(msg: types.Message, state: FSMContext) -> None:
    # database availability check
    if not check_connection():
        await msg.answer(SERVICE_UNAVAILABLE)
        await Homework.workspace.set()
        return
    await Homework.teacher_empty_hw.set()
    tch_table = models.utils.teacher.gen_table()
    if tch_table != None:
        await msg.answer(SELECT_TEACHER, reply_markup=tch_table)
        return
    await msg.answer(TEACHERS_NOT_FOUND)
    await Homework.workspace.set()


async def __process_add_empty(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    # check existed homework
    is_exist = models.utils.homework.get_by(
        callback_data["name"], date.today())
    if is_exist:
        is_exist.parse_message("Homework: #*nothing*")
        is_exist.update(is_exist.tasks)
        await callback_query.message.edit_text(HOMEWORK_ADDED)
        log(f"Added homework", callback_query.from_user.full_name)
        await Homework.workspace.set()
        return
    temp = models.Homework()
    temp.parse_message("Homework: #*nothing*")
    temp.create(callback_data["name"])
    await callback_query.message.edit_text(HOMEWORK_ADDED)
    log(f"Added homework", callback_query.from_user.full_name)
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

    # add empty homework
    dp.register_message_handler(
        __add_empty, IsPrivate(), commands=['addempty'], state=Homework.workspace)

    # attach files
    dp.register_message_handler(
        __get_files, IsPrivate(),
        content_types=['photo', 'document', 'text'],
        state=Homework.attachments
    )
    # callback handlers

    # show homework by date
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

    # show last actions
    dp.register_callback_query_handler(
        __process_actions_show_last, actions_show_all_callback.filter(), state=Homework.workspace)

    # select teacher for adding empty homework
    dp.register_callback_query_handler(
        __process_add_empty, choice_teacher_callback.filter(), state=Homework.teacher_empty_hw)
