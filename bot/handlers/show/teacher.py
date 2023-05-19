from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils.callback_data import CallbackData

from database.methods.select import teachers
from database.methods import delete
from models.utils.teacher import to_teacher
from models.teacher import Teacher

from ...utils.messages import TEACHERS_NOT_FOUND

from .helpers import edit_delete_ikb, edit_delete_callback

from ...filters import IsPrivate


async def __all(msg: Message, state: FSMContext):
    await state.reset_state(with_data=False)

    show_list: list[Teacher] = to_teacher(teachers())

    if isinstance(show_list, Teacher):
        await msg.answer(show_list.print(), reply_markup=edit_delete_ikb(show_list.id))
        return
    elif show_list == None:
        await msg.answer(TEACHERS_NOT_FOUND)
        return
    for item in show_list:
        await msg.answer(item.print(), reply_markup=edit_delete_ikb(item.id))


async def __process_all_actions(callback_query: CallbackQuery, callback_data: CallbackData):
    action = callback_data["act"]
    id = callback_data["id"]
    msg = callback_query.message

    if action == "EDIT":
        pass
    elif action == "DELETE":
        delete.teacher_by_id(int(id))
        await msg.delete()


def register_show_teacher_handlers(dp: Dispatcher):
    dp.register_message_handler(
        __all, IsPrivate(),  commands=['teachers'], state="*")

    # callbacks

    dp.register_callback_query_handler(
        __process_all_actions, edit_delete_callback.filter(), state="*")
