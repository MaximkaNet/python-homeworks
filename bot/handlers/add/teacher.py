from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.callback_data import CallbackData

from models import Teacher

from ...utils.messages import ADD_TEACHER, ADD_WORK_DAYS
from ...utils.messages import WORK_DAYS_IS_EMPTY
from ...utils.messages import COMPLETE_ADD_TEACHER
from ...utils.messages import SERVICE_UNAVAILABLE

from .state.teacher import TeacherState

from utils.selectweekdays import SelectWeekDays, week_days_callback

from ...filters import IsPrivate
from ...middlewares.check_connection_middleware import check_connection


async def __add(msg: Message, state: FSMContext):
    """
    Add new teacher
    """
    # check connection
    conn_msg, access = await check_connection()
    if not access:
        await msg.answer(conn_msg)
        return

    await state.reset_state(with_data=False)
    await msg.answer(ADD_TEACHER)
    await TeacherState.name.set()


async def __process_name(msg: Message, state: FSMContext):
    async with state.proxy() as teacherState:
        teacherState["name"] = msg.text

    await TeacherState.select_days.set()
    await msg.answer(ADD_WORK_DAYS, reply_markup=await SelectWeekDays().start())


async def __process_days(callback_query: CallbackQuery, callback_data: CallbackData, state: FSMContext):
    selected, days = await SelectWeekDays().process_select(callback_query, callback_data)
    if selected:
        if len(days) == 0:
            msg: Message = callback_query.message
            await msg.answer(WORK_DAYS_IS_EMPTY, reply_markup=await SelectWeekDays().start([]))
            return

        # add teacher into database
        async with state.proxy() as teacherState:
            name = teacherState["name"]
            work_days = days
            new_teacher = Teacher(id=None, name=name, work_days=work_days)
            new_teacher.create()

        # conplete message
        await callback_query.message.answer(COMPLETE_ADD_TEACHER)
        await state.finish()


async def __set_name(msg: Message, state: FSMContext) -> None:
    # check connection
    conn_msg, access = await check_connection()
    if not access:
        await msg.answer(conn_msg)
        return

    await msg.answer(SERVICE_UNAVAILABLE)


async def __set_work_days(msg: Message, state: FSMContext) -> None:
    # check connection
    conn_msg, access = await check_connection()
    if not access:
        await msg.answer(conn_msg)
        return

    await msg.answer(SERVICE_UNAVAILABLE)


def register_add_teacher_handlers(dp: Dispatcher):
    dp.register_message_handler(__add, IsPrivate(), commands=['newteacher'])
    dp.register_message_handler(__set_name, IsPrivate(), commands=['setname'])
    dp.register_message_handler(
        __set_work_days, IsPrivate(), commands=['setworkdays'])
    dp.register_message_handler(
        __process_name, IsPrivate(), state=TeacherState.name)

    # callbacks

    dp.register_callback_query_handler(
        __process_days, week_days_callback.filter(), state=TeacherState.select_days)
