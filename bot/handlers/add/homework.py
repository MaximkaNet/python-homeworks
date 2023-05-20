from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.callback_data import CallbackData

from ...utils.messages import SELECT_TEACHER, TEACHERS_NOT_FOUND, ADD_DATA_HOMEWORK
from ...utils.messages import SERVICE_UNAVAILABLE
from ...utils.messages import HOMEWORK_ALREADY_EXIST, HOMEWORK_HAS_BEEN_ADDED, HOMEWORK_INCORRECT_FORMAT, FILE_HAS_BEEN_ADDED

from .state.homework import HomeworkAddState

from models.homework import Homework
from models.teacher import Teacher
from models.utils.teacher import gen_table, choice_teacher_callback
from models.utils.teacher import to_teacher
from models.utils.homework import to_homework

from database.methods import select

from datetime import date

from ...filters import IsPrivate
from ...middlewares.check_connection_middleware import check_connection


async def __new(msg: Message, state: FSMContext):
    """
    Select a teacher for homework
    """
    await state.reset_state(with_data=False)

    # check connection
    conn_msg, access = await check_connection()
    if not access:
        await msg.answer(conn_msg)
        return

    await state.set_data({"homework": None, "main_msg": None})
    teachers_table = gen_table()
    if teachers_table != None:
        await msg.answer(
            SELECT_TEACHER,
            reply_markup=teachers_table
        )
        return
    await msg.answer(TEACHERS_NOT_FOUND)


async def __new_by_date(msg: Message, state: FSMContext):
    """
    Select a teacher for homework to selected date
    """

    await msg.answer(SERVICE_UNAVAILABLE)


async def __process_selected_teacher(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    """
    Create a homework object and add it to state
    """

    # check homework
    teachers: list[Teacher] = to_teacher(
        select.teacher_by_id(callback_data["id"]))
    current_date = date.today()
    candidates = to_homework(select.homework_by(
        teacher_id=teachers[0].id, date=current_date))
    if candidates != None:
        # edit homework ...
        await callback_query.message.edit_text(HOMEWORK_ALREADY_EXIST)
        await state.finish()
        return
        # /----

    homework = Homework(teacher=teachers[0].name)

    await state.update_data({"homework": homework, "main_msg": callback_query.message, "teacher_id": teachers[0].id})

    await callback_query.message.edit_text(ADD_DATA_HOMEWORK, reply_markup=None)

    await HomeworkAddState.homework.set()


async def __add_data(msg: Message, state: FSMContext):
    """
    Add tasks
    """
    # parse message
    async with state.proxy() as homeworkState:
        homework: Homework = homeworkState["homework"]
        main_msg: Message = homeworkState["main_msg"]
        teacher_id: int = homeworkState["teacher_id"]
        if homework.parse_message(msg.text):
            # insert homework
            selected_date = date.today()
            homework.create(selected_date, teacher_id=teacher_id)
            # -----
            await main_msg.edit_text(f"{homework.print()}\n{HOMEWORK_HAS_BEEN_ADDED}")
            await HomeworkAddState.attachments.set()
        else:
            try:
                await main_msg.edit_text(f"{ADD_DATA_HOMEWORK}\n*{HOMEWORK_INCORRECT_FORMAT}*")
            except:
                pass
    await msg.delete()


async def __add_attachments(msg: Message, state: FSMContext):
    """
    Add attachments
    """
    loading = await msg.answer("Loading file...")
    homework: Homework = None
    async with state.proxy() as homeworkState:
        homework: Homework = homeworkState["homework"]
    await homework.add_attachment(msg)
    await loading.edit_text(FILE_HAS_BEEN_ADDED)
    await msg.delete()


def register_add_homework_handlers(dp: Dispatcher):
    dp.register_message_handler(__new,
                                IsPrivate(),
                                commands=['newhw'],
                                state="*")

    dp.register_message_handler(__new_by_date,
                                IsPrivate(),
                                commands=['newhwdate'],
                                state="*")

    dp.register_message_handler(__add_data,
                                content_types=['text'],
                                state=HomeworkAddState.homework)

    dp.register_message_handler(__add_attachments,
                                content_types=['photo', 'document'],
                                state=HomeworkAddState.attachments)

    # callbacks

    dp.register_callback_query_handler(__process_selected_teacher,
                                       choice_teacher_callback.filter(),
                                       state="*")
