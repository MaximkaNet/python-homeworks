from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters import Filter
from aiogram.utils.callback_data import CallbackData
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from datetime import date, timedelta
from homework import Homework
from datetime import datetime
from aiogram_calendar import dialog_cal_callback, DialogCalendar
from helpers import week_days_callback, SelectWeekDays

import config
import utils
import homework
import messages
import states
import teacher
import db
import json


bot = Bot(
    config.TOKEN,
    # proxy=config.PROXY_URL
)

dp = Dispatcher(bot, storage=MemoryStorage())

bot_mode = "user"


class IsPrivate(Filter):
    key = "chat_type_private"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "private" else False


class IsGroup(Filter):
    key = "chat_type_group_or_supergroup"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "group" or message.chat.type == "supergroup" else False


async def on_shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


@dp.message_handler(IsPrivate(), commands=['start', 'help'])
async def start_command_user(message: types.Message):
    await message.answer(messages.WELLCOME_USER, parse_mode=config.PARSE_MODE)


@dp.message_handler(IsGroup(), commands=['start', 'help'])
async def start_command_group(message: types.Message):
    await message.answer(messages.WELLCOME_GROUP, parse_mode=config.PARSE_MODE)


@dp.message_handler(IsPrivate(), commands=['addh'], state="*")
async def help_add_command(message: types.Message):
    await message.answer(messages.HELP_ADD, parse_mode=config.PARSE_MODE)

show_homework_callback = CallbackData("show_homework", "act", "src")


@dp.message_handler(IsGroup(), commands=['homework'], state="*")
async def homework_command(message: types.Message):
    await states.Homework.show.set()
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton("Tomorrow", callback_data=show_homework_callback.new("tomorrow", "group")),
            InlineKeyboardButton("Another", callback_data=show_homework_callback.new("another", "group")))
    await message.reply("Select a date:", reply_markup=ikb, parse_mode=config.PARSE_MODE)


@dp.message_handler(IsPrivate(), commands=['homework'], state="*")
async def homework_panel(message: types.Message):
    await states.Homework.workspace.set()
    await message.answer(f"{messages.HOMEWORK_PANEL_WELLCOME}\n\n{messages.HW_PANEL_COMMANDS}", parse_mode=config.PARSE_MODE)


@dp.message_handler(commands=['help'], state=states.Homework.workspace)
async def cmd_help_homework(message: types.Message):
    await message.answer(messages.HW_PANEL_COMMANDS, parse_mode=config.PARSE_MODE)


@dp.message_handler(commands=['show'], state=states.Homework.workspace)
async def cmd_show_homework(message: types.Message):
    await states.Homework.show.set()
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton("Tomorrow", callback_data=show_homework_callback.new("tomorrow", "private")),
            InlineKeyboardButton("Another", callback_data=show_homework_callback.new("another", "private")))
    await message.reply("Select a date:", reply_markup=ikb, parse_mode=config.PARSE_MODE)


@dp.callback_query_handler(show_homework_callback.filter(), state=states.Homework.show)
async def process_show_homework(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    if callback_data["act"] == "tomorrow":
        selected_date: date = date.today() + timedelta(days=1)
        # loading..
        wrapper = f"*Loading...*\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
        # find homeworks
        show_list: list[Homework] = homework.get_last_by_date(selected_date)
        await callback_query.message.edit_text(
            wrapper, reply_markup=None, parse_mode=config.PARSE_MODE)
        if len(show_list) == 0:
            wrapper = f"*{messages.HOMEWORKS_NOT_FOUND}*\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
            await callback_query.message.edit_text(wrapper, reply_markup=None, parse_mode=config.PARSE_MODE)
            await state.finish()
            if callback_data["src"] == "private":
                await states.Homework.workspace.set()
            return
        # print results
        wrapper = f"{show_list[0].print()}\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(wrapper,
                                               reply_markup=None, parse_mode=config.PARSE_MODE)
        for show_item in range(1, len(show_list)):
            wrapper = f"{show_item.print()}\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
            await callback_query.message.answer(wrapper, parse_mode=config.PARSE_MODE)
        await state.finish()
        if callback_data["src"] == "private":
            await states.Homework.workspace.set()
    elif callback_data["act"] == "another":
        await callback_query.message.edit_reply_markup(await DialogCalendar().start_calendar())
        await state.finish()
        if callback_data["src"] == "private":
            await states.Homework.workspace.set()


@dp.callback_query_handler(dialog_cal_callback.filter(), state="*")
async def process_show_calendar(callback_query: types.CallbackQuery, callback_data: CallbackData):
    _selected, _date = await DialogCalendar().process_selection(callback_query, callback_data)
    if _selected:
        selected_date: date = _date.date()
        # find homeworks
        show_list: list[Homework] = homework.get_last_by_date(selected_date)
        # loading..
        wrapper = f"*Loading...*\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(
            wrapper, reply_markup=None, parse_mode=config.PARSE_MODE)
        if len(show_list) == 0:
            wrapper = f"*{messages.HOMEWORKS_NOT_FOUND}*\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
            await callback_query.message.edit_text(wrapper, reply_markup=None, parse_mode=config.PARSE_MODE)
            return
        # print results
        wrapper = f"{show_list[0].print()}\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(wrapper,
                                               reply_markup=None, parse_mode=config.PARSE_MODE)
        for show_item in range(1, len(show_list)):
            wrapper = f"{show_item.print()}\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
            await callback_query.message.answer(wrapper, parse_mode=config.PARSE_MODE)


@dp.message_handler(commands=['add'], state=states.Homework.workspace)
async def cmd_add_homework(message: types.Message, state: FSMContext):
    await states.Homework.teacher.set()
    table = teacher.gen_table()
    if table != None:
        await message.answer(messages.SELECT_TEACHER, reply_markup=table, parse_mode=config.PARSE_MODE)
        return
    await message.answer(f"{messages.TEACHERS_NOT_FOUND}\nCommands: /help", parse_mode=config.PARSE_MODE)
    await state.finish()
    await states.Homework.workspace.set()


@dp.callback_query_handler(teacher.choice_teacher_callback.filter(), state=states.Homework.teacher)
async def process_teacher(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    async with state.proxy() as data:
        data["teacher"] = callback_data["name"]
        data["add_date"] = date.today()
        selected_teacher = f"{messages.SELECT_TEACHER} _{data['teacher']}_"
        await callback_query.message.edit_text(selected_teacher, parse_mode=config.PARSE_MODE)
        # check existed homework
        is_exist = homework.get_by(data["teacher"], data["add_date"])
        if is_exist:
            data["homework"] = is_exist
            await states.Homework.edit_question.set()
            await callback_query.message.edit_text(
                f"{selected_teacher}\n\n{messages.HOMEWORK_UPDATE_QUESTION}", parse_mode=config.PARSE_MODE)
            return
        await callback_query.message.edit_text(f"{selected_teacher}\n{messages.ADD_TASK}", parse_mode=config.PARSE_MODE)
        await states.Homework.work.set()


@dp.message_handler(state=states.Homework.edit_question)
async def edit_question_homework(message: types.Message, state: FSMContext):
    if message.text.lower() == "yes":
        async with state.proxy() as data:
            homework: Homework = data["homework"]
            selected_teacher = f"{messages.SELECT_TEACHER} _{data['teacher']}_"
            if homework:
                await message.answer(f"{selected_teacher}\n{messages.ADD_TASK}", parse_mode=config.PARSE_MODE)
                await message.answer(homework.convert_tasks())
                await states.Homework.edit.set()
    else:
        await message.answer(messages.ACTION_CANCELED)
        await state.finish()
        await states.Homework.workspace.set()


@dp.message_handler(state=states.Homework.edit)
async def edit_homework(message: types.Message, state: FSMContext) -> int:
    if message.text == "/cancel":
        await message.answer(messages.ACTION_CANCELED)
        await state.finish()
        await states.Homework.workspace.set()
        return
    elif message.text == "/hadd":
        await message.answer(messages.HELP_ADD, parse_mode=config.PARSE_MODE)
        return
    temp_homework = Homework()
    isValid = temp_homework.parse_message(message.text)
    if isValid:
        async with state.proxy() as data:
            homework: Homework = data["homework"]
            homework.update(temp_homework.tasks)
            utils.log(edit_homework, "Update homework",
                      user=f"{message.from_user.full_name} ({message.from_user.username})")
            await message.answer(messages.HOMEWORK_EDITED)
            await state.finish()
            await states.Homework.workspace.set()
            return
    else:
        await message.answer(messages.INCORRECT)
        await message.answer(messages.ADD_TASK, parse_mode=config.PARSE_MODE)
        return


@dp.message_handler(state=states.Homework.work)
async def process_work(message: types.Message, state: FSMContext):
    if message.text == "/hadd":
        await message.answer(messages.HELP_ADD, parse_mode=config.PARSE_MODE)
        return
    if message.text == "/cancel":
        await message.answer(messages.ACTION_CANCELED)
        await state.finish()
        await states.Homework.workspace.set()
        return
    async with state.proxy()as data:
        temp_obj = Homework()
        isValid = temp_obj.parse_message(message.text)
        if isValid:
            temp_obj.create(data["teacher"])
            await message.answer(messages.HOMEWORK_ADDED)
            utils.log(process_work, "Create homework",
                      user=f"{message.from_user.full_name} ({message.from_user.username})")
            await state.finish()
            await states.Homework.workspace.set()
        else:
            await message.answer(messages.INCORRECT)
            await message.answer(messages.ADD_TASK, parse_mode=config.PARSE_MODE)
            await states.Homework.work.set()

showall_callback = CallbackData("all", "action", "author", "date")


@dp.message_handler(IsPrivate(), filters.RegexpCommandsFilter(regexp_commands=['showlast([0-9]*)']), state=states.Homework.workspace)
async def homework_show_last(message: types.Message, regexp_command, state: FSMContext):
    count_hw = int(regexp_command.group(1)) if regexp_command.group(
        1) and int(regexp_command.group(1)) > 0 else 2
    await states.Homework.show_last.set()
    async with state.proxy() as data:
        data["show_last"] = count_hw
    await message.answer(messages.SELECT_TEACHER, reply_markup=teacher.gen_table(), parse_mode=config.PARSE_MODE)


@dp.callback_query_handler(teacher.choice_teacher_callback.filter(), state=states.Homework.show_last)
async def process_teacher_homework(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    _count_hw: int = 2
    async with state.proxy() as data:
        _count_hw = data["show_last"]
    _teacher: str = callback_data["name"]
    _homeworks: list[Homework] = homework.convert_to_list(
        db.select_homeworks(limit=_count_hw, author=_teacher))
    if len(_homeworks) == 0:
        await callback_query.message.edit_text(messages.HOMEWORKS_NOT_FOUND)
        await state.finish()
        await states.Homework.workspace.set()
        return
    for i, item in enumerate(_homeworks):
        actions = InlineKeyboardMarkup()
        callback_edit = showall_callback.new(
            "EDIT", f"{item.author}", f"{item.date.strftime(config.DATE_FORMAT)}")
        callback_delete = showall_callback.new(
            "DELETE", f"{item.author}", f"{item.date.strftime(config.DATE_FORMAT)}")
        edit = InlineKeyboardButton(
            "Edit", callback_data=callback_edit)
        delete = InlineKeyboardButton(
            "Delete", callback_data=callback_delete)
        actions.add(edit, delete)
        if i == 0:
            await callback_query.message.edit_text(item.print(), reply_markup=actions, parse_mode=config.PARSE_MODE)
            continue
        await callback_query.message.answer(item.print(), reply_markup=actions, parse_mode=config.PARSE_MODE)
    await state.finish()
    await states.Homework.workspace.set()


@dp.callback_query_handler(showall_callback.filter(), state=states.Homework.workspace)
async def process_homeworks_actions(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    if (callback_data["action"] == "EDIT"):
        async with state.proxy() as data:
            date = datetime.strptime(
                callback_data["date"], config.DATE_FORMAT).date()
            _homework: Homework = homework.get_by(
                callback_data["author"], date)
            data["homework"] = _homework
            selected_teacher = f"{messages.SELECT_TEACHER} _{callback_data['author']}_"
            if _homework:
                await callback_query.message.answer(f"{selected_teacher}\n{messages.ADD_TASK}", parse_mode=config.PARSE_MODE)
                await callback_query.message.answer(_homework.convert_tasks())
                await states.Homework.edit.set()
    else:
        date = datetime.strptime(
            callback_data["date"], config.DATE_FORMAT).date()
        delete_homework = homework.get_by(callback_data["author"], date)
        if not delete_homework:
            utils.debug(process_homeworks_actions, "Obj not found.")
            await callback_query.message.delete()
            await state.finish()
            await states.Homework.workspace.set()
            return
        db.delete_homework(date, callback_data["author"])
        await callback_query.message.edit_text(messages.HOMEWORK_DELETED)
        await state.finish()
        await states.Homework.workspace.set()


@dp.message_handler(IsPrivate(), commands=['close'], state=states.Homework.workspace)
async def cmd_close_homework(message: types.Message, state: FSMContext):
    await message.answer(messages.HOMEWORK_PANEL_BYE, parse_mode=config.PARSE_MODE)
    await state.finish()


@dp.message_handler(IsPrivate(), commands=['teacher'])
async def cmd_teacher(message: types.Message):
    await states.Teacher.workspace.set()
    await message.answer(f"{messages.TEACHER_PANEL_WELLCOME}\n\n{messages.TCH_PANEL_COMMANDS}", parse_mode=config.PARSE_MODE)


@dp.message_handler(IsPrivate(), commands=['help'], state=states.Teacher.workspace)
async def cmd_help_teacher(message: types.Message):
    await message.answer(messages.TCH_PANEL_COMMANDS)

show_teacher_actions = CallbackData(
    "teacher_show_actions", "act", "name", "work_days")


@dp.message_handler(commands=["show"], state=states.Teacher.workspace)
async def cmd_show(message: types.Message):
    teachers = teacher.convert_to_list(db.select_teachers())

    for item in teachers:
        act_kb = InlineKeyboardMarkup(row_width=2)
        act_kb.row()
        act_kb.insert(InlineKeyboardButton(
            "Edit", callback_data=show_teacher_actions.new("EDIT", item.name, json.dumps(item.work_days))))
        act_kb.insert(InlineKeyboardButton(
            "Delete", callback_data=show_teacher_actions.new("DELETE", item.name, "[]")))
        await message.answer(item.print(), reply_markup=act_kb, parse_mode=config.PARSE_MODE)


@dp.callback_query_handler(show_teacher_actions.filter(), state=states.Teacher.workspace)
async def actions_show(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    if callback_data["act"] == "EDIT":
        async with state.proxy() as data:
            data["name"] = callback_data["name"]
        _teacher = callback_data["name"]
        work_days = json.loads(callback_data["work_days"])
        await callback_query.message.edit_text(f"Selected teacher: {_teacher}\nNow choose working day(s), where the teacher works.\n_Selected days: _" + ", ".join(map(str, utils.convert_week(work_days))), reply_markup=await SelectWeekDays().start(), parse_mode=config.PARSE_MODE)
    elif callback_data["act"] == "DELETE":
        delete_teacher = teacher.convert_to_list(
            db.select_teacher_by(callback_data["name"]))
        if not len(delete_teacher):
            utils.debug(actions_show, "Obj not found.")
            await callback_query.message.delete()
            await state.finish()
            await states.Teacher.workspace.set()
            return
        db.delete_teacher(callback_data["name"])
        await callback_query.message.delete()


@dp.callback_query_handler(week_days_callback.filter(), state=states.Teacher.workspace)
async def actions_edit(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, days = await SelectWeekDays().process_select(callback_query, callback_data)
    if selected:
        async with state.proxy() as data:
            db.update_teacher(data["name"], days)
        act_kb = InlineKeyboardMarkup(row_width=2)
        act_kb.row()
        act_kb.insert(InlineKeyboardButton(
            "Edit", callback_data=show_teacher_actions.new("EDIT", data["name"], days)))
        act_kb.insert(InlineKeyboardButton(
            "Delete", callback_data=show_teacher_actions.new("DELETE", data["name"], [])))
        _teacher = teacher.convert_to_list(db.select_teacher_by(data["name"]))
        if len(_teacher):
            await callback_query.message.edit_text(_teacher[0].print(), reply_markup=act_kb, parse_mode=config.PARSE_MODE)


@dp.message_handler(commands=['add'], state=states.Teacher.workspace)
async def cmd_add(message: types.Message):
    await message.answer("Type the teacher name:")
    await states.Teacher.name.set()


@dp.message_handler(state=states.Teacher.name)
async def add_teacher(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
        await states.Teacher.work_days.set()
        await message.answer("Now choose working day(s), where the teacher works.", reply_markup=await SelectWeekDays([]).start())


@dp.callback_query_handler(week_days_callback.filter(), state=states.Teacher.work_days)
async def process_select_days(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, days = await SelectWeekDays().process_select(callback_query, callback_data)
    if selected:
        if not len(days):
            await callback_query.message.edit_text(messages.ACTION_CANCELED, parse_mode=config.PARSE_MODE)
        else:
            async with state.proxy() as data:
                name = data["name"]
                db.insert_teacher(name, days)
                await callback_query.message.answer(messages.TEACHER_ADDED)
        await state.finish()
        await states.Teacher.workspace.set()


@dp.message_handler(commands=['changename'], state=states.Teacher.workspace)
async def cmd_change_name(message: types.Message):
    await message.answer("Select a teacher:", reply_markup=teacher.gen_table())


@dp.callback_query_handler(teacher.choice_teacher_callback.filter(), state=states.Teacher.workspace)
async def process_change_name(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    teacher_name = callback_data["name"]
    await callback_query.message.edit_text(f"Selected teacher: *{teacher_name}*\nType new name.", parse_mode=config.PARSE_MODE)
    async with state.proxy() as data:
        data["name"] = callback_data["name"]
    await states.Teacher.change_name.set()


@dp.message_handler(state=states.Teacher.change_name)
async def change_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        db.update_teacher(data["name"], new_name=message.text)
    await state.finish()
    await states.Teacher.workspace.set()
    await message.answer(messages.TEACHER_EDITED)


@dp.message_handler(commands=["close"], state=states.Teacher.workspace)
async def close_teacher_ws(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(messages.TEACHER_PANEL_BYE, parse_mode=config.PARSE_MODE)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
