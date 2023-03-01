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
    key = "chat_type_private"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "private" else False


class IsGroup(Filter):
    key = "chat_type_group_or_supergroup"

    async def check(self, message: types.Message) -> bool:
        return True if message.chat.type == "group" or message.chat.type == "supergroup" else False


async def on_shutdown(dispatcher: Dispatcher):
    await bot.delete_my_commands()
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

show_homework_callback = CallbackData("show_homework_1", "act", "src")


@dp.message_handler(IsGroup(), commands=['homework'])
async def homework_command(message: types.Message):
    ikb = InlineKeyboardMarkup()
    ikb.add(InlineKeyboardButton("Tomorrow", callback_data=show_homework_callback.new("tomorrow", "group")),
            InlineKeyboardButton("Another", callback_data=show_homework_callback.new("another", "group")))
    await message.reply("Select a date:", reply_markup=ikb, parse_mode=config.PARSE_MODE)


@dp.message_handler(IsPrivate(), commands=['homework'])
async def homework_panel(message: types.Message):
    await states.Homework.workspace.set()
    await message.answer(messages.HOMEWORK_PANEL_WELLCOME)


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
        # find homeworks
        show_list: list[Homework] = homework.get_last_by_date(selected_date)
        # loading..
        wrapper = f"*Loading...*\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
        await callback_query.message.edit_text(
            wrapper, reply_markup=None, parse_mode=config.PARSE_MODE)
        if len(show_list) == 0:
            wrapper = f"*Homeworks not found.*\n_Selected date: {selected_date.strftime(config.DATE_FORMAT)}_"
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


@dp.message_handler(commands=['add'], state=states.Homework.workspace)
async def cmd_add_homework(message: types.Message, state: FSMContext):
    await states.Homework.teacher.set()
    table = teacher.gen_table()
    if table != None:
        await message.answer(messages.SELECT_TEACHER, reply_markup=table, parse_mode=config.PARSE_MODE)
        return
    await message.answer("Teachers not found", parse_mode=config.PARSE_MODE)
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
            await message.answer("Complete!")
            await state.finish()
            await states.Homework.workspace.set()
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
        await states.Homework.workspace.set()
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
            await states.Homework.workspace.set()
        else:
            await message.answer("Incorrect answer!")
            await message.answer(messages.ADD_TASK, parse_mode=config.PARSE_MODE)
            await states.Homework.work.set()

showall_callback = CallbackData("all", "action", "author", "date")


@dp.message_handler(IsPrivate(), commands=['showall'], state=states.Homework.workspace)
async def cmd_showall_homework(message: types.Message):
    items = homework.convert_to_list(db.select_homeworks())
    if len(items) == 0:
        await message.answer("Homeworks not found")
        return
    for item in items:
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
        await message.answer(item.print(), reply_markup=actions, parse_mode=config.PARSE_MODE)


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
            await callback_query.message.edit_text("Error: May be object was deleted.")
            await state.finish()
            await states.Homework.workspace.set()
            return
        db.delete_homework(date, callback_data["author"])
        await callback_query.message.edit_text("Deleted.")
        await state.finish()
        await states.Homework.workspace.set()


@dp.message_handler(IsPrivate(), commands=['close'], state=states.Homework.workspace)
async def cmd_close_homework(message: types.Message, state: FSMContext):
    await message.answer("*Homework* managment panel was closed.", parse_mode=config.PARSE_MODE)
    await state.finish()

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
