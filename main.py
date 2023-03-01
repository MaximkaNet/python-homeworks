from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
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


bot = Bot(
    config.TOKEN,
    # proxy=config.PROXY_URL
)

dp = Dispatcher(bot, storage=MemoryStorage())

bot_mode = "user"


class IsPrivate(Filter):
    key = "chat_type"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "private" else False


class IsGroup(Filter):
    key = "chat_type"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "group" else False


async def on_shutdown(dispatcher: Dispatcher):
    await bot.delete_my_commands()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


@dp.message_handler(IsPrivate(), commands=['start', 'help'])
async def start_command(message: types.Message):
    await message.answer(messages.WELLCOME_USER, parse_mode=config.PARSE_MODE)


@dp.message_handler(IsGroup(), commands=['start', 'help'])
async def start_command(message: types.Message):
    await message.answer(messages.WELLCOME_GROUP, parse_mode=config.PARSE_MODE)


@dp.message_handler(IsPrivate(), commands=['hadd'])
async def help_add_command(message: types.Message):
    await message.answer(messages.HELP_ADD, parse_mode=config.PARSE_MODE)


@dp.message_handler(commands=['homework'])
async def homework_command(message: types.Message):
    await states.ShowHomework.select.set()
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton("Tomorrow", callback_data="tomorrow"),
            InlineKeyboardButton("Another", callback_data="another"))
    await message.reply("Select a date:", reply_markup=ikb, parse_mode=config.PARSE_MODE)


@dp.callback_query_handler(state=states.ShowHomework.select)
async def process_show_homework(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == "tomorrow":
        selected_date: date = date.today() + timedelta(days=1)
        # find homeworks
        show_list: list[Homework] = homework.get_last_by_date(selected_date)
        # loading..
        wrapper = f"*Loading...*\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
        await callback.message.edit_text(
            wrapper, reply_markup=None, parse_mode=config.PARSE_MODE)
        if len(show_list) == 0:
            wrapper = f"*Homeworks not found.*\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
            await callback.message.edit_text(wrapper, reply_markup=None, parse_mode=config.PARSE_MODE)
            await state.finish()
            return
        # print results
        wrapper = f"{show_list[0].print()}\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
        await callback.message.edit_text(wrapper,
                                         reply_markup=None, parse_mode=config.PARSE_MODE)
        for show_item in range(1, len(show_list)):
            wrapper = f"{show_item.print()}\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
            await callback.message.answer(wrapper, parse_mode=config.PARSE_MODE)
        await state.finish()
    elif callback.data == "another":
        await callback.message.edit_reply_markup(await DialogCalendar().start_calendar())
        await state.finish()


@dp.callback_query_handler(dialog_cal_callback.filter())
async def process_show_calendar(callback_query: types.CallbackQuery, callback_data: dict):
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
            wrapper = f"*Homeworks not found.*\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
            await callback_query.message.edit_text(wrapper, reply_markup=None, parse_mode=config.PARSE_MODE)
            return
        # print results
        wrapper = f"{show_list[0].print()}\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(wrapper,
                                               reply_markup=None, parse_mode=config.PARSE_MODE)
        for show_item in range(1, len(show_list)):
            wrapper = f"{show_item.print()}\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
            await callback_query.message.answer(wrapper, parse_mode=config.PARSE_MODE)


@dp.message_handler(IsPrivate(), commands=['add'])
async def add_command(message: types.Message):
    await states.Homework.teacher.set()
    table = teacher.gen_table()
    if table != None:
        await message.answer(messages.SELECT_TEACHER, reply_markup=table, parse_mode=config.PARSE_MODE)
        return
    await message.answer("Teachers not found", parse_mode=config.PARSE_MODE)


@dp.callback_query_handler(teacher.choice_teacher.filter(), state=states.Homework.teacher)
async def process_teacher(callback_query: types.CallbackQuery, callback_data: dict, state: FSMContext):
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
                f"{selected_teacher}\n\nHomework already exist.\nDo you want to edit homework?\n*yes / no*", parse_mode=config.PARSE_MODE)
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


@dp.message_handler(state=states.Homework.edit)
async def update_homework(message: types.Message, state: FSMContext) -> int:
    if message.text == "/cancel":
        await message.answer(messages.ACTION_CANCELED)
        await state.finish()
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
            utils.log(update_homework, "Update homework",
                      user=f"{message.from_user.full_name} ({message.from_user.username})")
            await message.answer("Complete!")
            await state.finish()
            return
    else:
        await message.answer("Incorrect answer!")
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
        return
    async with state.proxy()as data:
        temp_obj = Homework()
        isValid = temp_obj.parse_message(message.text)
        if isValid:
            temp_obj.create(data["teacher"])
            await message.answer("Complete!")
            utils.log(process_work, "Create homework",
                      user=f"{message.from_user.full_name} ({message.from_user.username})")
            await state.finish()
        else:
            await message.answer("Incorrect answer!")
            await message.answer(messages.ADD_TASK, parse_mode=config.PARSE_MODE)
            await states.Homework.work.set()

all_actions = CallbackData("all", "action", "author", "date")


@dp.message_handler(IsPrivate(), commands=['all'])
async def all_command(message: types.Message):
    items = homework.convert_to_list(db.select_homeworks())
    if len(items) == 0:
        await message.answer("Homeworks not found")
        return
    for item in items:
        actions = InlineKeyboardMarkup()
        callback_edit = all_actions.new(
            "edit", f"{item.author}", f"{item.date.strftime(config.DATE_FORMAT)}")
        callback_delete = all_actions.new(
            "delete", f"{item.author}", f"{item.date.strftime(config.DATE_FORMAT)}")
        edit = InlineKeyboardButton(
            "Edit", callback_data=callback_edit)
        delete = InlineKeyboardButton(
            "Delete", callback_data=callback_delete)
        actions.add(edit, delete)
        await message.answer(item.print(), reply_markup=actions, parse_mode=config.PARSE_MODE)


@dp.callback_query_handler(all_actions.filter())
async def homeworks_actions(callback: types.CallbackQuery, callback_data, state: FSMContext):
    if (callback_data["action"] == "edit"):
        date = datetime.strptime(
            callback_data["date"], config.DATE_FORMAT).date()
        edit_homework = homework.get_by(callback_data["author"], date)
        if edit_homework:
            async with state.proxy() as data:
                data["edit_obj"] = edit_homework
                data["teacher"] = callback_data["author"]
                await callback.message.answer(messages.ADD_TASK, parse_mode=config.PARSE_MODE)
                await callback.message.answer("You edit homework:")
                await callback.message.answer(edit_homework.convert_tasks(), parse_mode=config.PARSE_MODE)
                await states.Print.edit.set()
    else:
        date = datetime.strptime(
            callback_data["date"], config.DATE_FORMAT).date()
        delete_homework = homework.get_by(callback_data["author"], date)
        if not delete_homework:
            utils.debug(homeworks_actions, "Obj not found.")
            await callback.message.edit_text("Error: May be object was deleted.")
            await state.finish()
            return
        db.delete_homework(date, callback_data["author"])
        await callback.message.edit_text("Deleted.")
        await state.finish()


@dp.message_handler(state=states.Print.edit)
async def edit_homework(message: types.Message, state: FSMContext):
    if message.text == "/cancel":
        await message.answer(messages.ACTION_CANCELED)
        await state.finish()
        return
    elif message.text == "/hadd":
        await message.answer(messages.HELP_ADD, parse_mode=config.PARSE_MODE)
        return
    temp_homework = Homework()
    isValid = temp_homework.parse_message(message.text)
    if isValid:
        async with state.proxy() as data:
            homework: Homework = data["edit_obj"]
            homework.update(temp_homework.tasks)
        await message.answer("Complete!")
        utils.log(edit_homework, "Update homework",
                  user=f"{message.from_user.full_name} ({message.from_user.username})")
        await state.finish()
    else:
        await message.answer("Incorrect answer!")
        await message.answer(messages.ADD_TASK, parse_mode=config.PARSE_MODE)
        await message.answer("You can /cancel edit homework.")


@dp.message_handler(IsPrivate(), commands=['teacher'])
async def cmd_teacher(message: types.Message):
    await states.Teacher.workspace.set()
    await message.answer(messages.WELLCOME_TEACHER_WORKSPACE, parse_mode=config.PARSE_MODE)

show_teacher_actions = CallbackData(
    "teacher_show_actions", "act", "name", "work_days")


@dp.message_handler(commands=["show"], state=states.Teacher.workspace)
async def cmd_show(message: types.Message):
    teachers = teacher.convert_to_list(db.select_teachers())

    for item in teachers:
        act_kb = InlineKeyboardMarkup(row_width=2)
        act_kb.row()
        act_kb.insert(InlineKeyboardButton(
            "Edit", callback_data=show_teacher_actions.new("EDIT", item.name, item.work_days)))
        act_kb.insert(InlineKeyboardButton(
            "Delete", callback_data=show_teacher_actions.new("DELETE", item.name, [])))
        await message.answer(item.print(), reply_markup=act_kb, parse_mode=config.PARSE_MODE)


@dp.callback_query_handler(show_teacher_actions.filter(), state=states.Teacher.workspace)
async def actions_show(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    if callback_data["act"] == "EDIT":
        async with state.proxy() as data:
            data["name"] = callback_data["name"]
        teacher = callback_data["name"]
        work_days = callback_data["work_days"]
        await callback_query.message.answer(f"Selected teacher: {teacher}")
        await callback_query.message.answer("Now choose working day(s), where the teacher works.", reply_markup=await SelectWeekDays(selected_days=work_days).start())
    elif callback_data["act"] == "DELETE":
        db.delete_teacher(callback_data["name"])
        await callback_query.message.edit_text("Deleted.")


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
        await message.answer("Now choose working day(s), where the teacher works.", reply_markup=await SelectWeekDays().start())


@dp.callback_query_handler(week_days_callback.filter(), state=states.Teacher.work_days)
async def process_select_days(callback_query: types.CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, days = await SelectWeekDays().process_select(callback_query, callback_data)
    if selected:
        if days == None:
            await callback_query.message.edit_text(messages.ACTION_CANCELED, parse_mode=config.PARSE_MODE)
        else:
            async with state.proxy() as data:
                name = data["name"]
                db.insert_teacher(name, days)
                await callback_query.message.answer("Complete!")
        await state.finish()
        await states.Teacher.workspace.set()


@dp.message_handler(commands=['changename'], state=states.Teacher.workspace)
async def cmd_change_name(message: types.Message):
    await message.answer("Select a teacher:", reply_markup=teacher.gen_table())


@dp.callback_query_handler(teacher.choice_teacher.filter(), state=states.Teacher.workspace)
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
    await message.answer("Complete!")


@dp.message_handler(commands=["close"], state=states.Teacher.workspace)
async def close_teacher_ws(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Teacher workspace was closed.")
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
