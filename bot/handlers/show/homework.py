from aiogram.dispatcher import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.storage import FSMContext

from aiogram_calendar import DialogCalendar, dialog_cal_callback
from datetime import date, timedelta

from ...utils import show_selected_wrapper, show_add_wrapper, show_updated_wrapper
from ...utils.messages import HOMEWORKS_NOT_FOUND

from models import Homework
from models.utils.homework import get_last_by_date, to_homework
from models.utils.attachment import to_attachment

from database.methods.select import homeworks
from database.methods import count
from database.methods import delete
from database.methods import select

from .helpers.infinity_list import gen_load_more, infinity_list_callback
from .helpers.edit_delete_ikb_hw import list_actions_ikb, list_actions_hw_callback

from ...middlewares import check_connection

from ...filters import IsPrivate


async def __template_show(msg: Message, objs: Homework | list[Homework], selected_date: date = None):
    if isinstance(objs, Homework):
        # print results
        if selected_date != None:
            await msg.answer(show_selected_wrapper(objs.print(), selected_date),
                             reply_markup=None)
        else:
            await msg.answer(objs.print(count_attachments=count.attachments(objs.id)),
                             reply_markup=None)

        # show attachments
        await objs.show_attachments(msg)
        return

    # print results
    if selected_date != None:
        await msg.edit_text(show_selected_wrapper(objs[0].print(), selected_date),
                            reply_markup=None)
    else:
        await msg.edit_text(objs[0].print(),
                            reply_markup=None)

    # show attachments
    await objs[0].show_attachments(msg)

    # print results
    for i in range(1, len(objs)):
        if selected_date != None:
            await msg.answer(show_selected_wrapper(
                objs[i].print(),
                selected_date))
        else:
            await msg.answer(objs[i].print())
        await objs[i].show_attachments(msg)


async def __tomorrow(msg: Message, state: FSMContext) -> None:
    """
    Get homeworks
    """
    await state.reset_state(with_data=False)
    selected_date: date = date.today() + timedelta(days=1)

    # loading...
    LOADING_MSG = "*Loading...*"
    wrapp_msg = await msg.answer(show_selected_wrapper(LOADING_MSG, selected_date))

    # check connection
    conn_msg, access = await check_connection()
    if not access:
        await wrapp_msg.edit_text(conn_msg)
        return

    # find homeworks
    show_list: list[Homework] = get_last_by_date(selected_date)
    if show_list == None:
        await wrapp_msg.edit_text(show_selected_wrapper(HOMEWORKS_NOT_FOUND, selected_date))
        return

    # print results
    await __template_show(wrapp_msg, show_list, selected_date=selected_date)


async def __last_by_teacher(msg: Message) -> None:
    pass


async def __another_date(msg: Message, state: FSMContext) -> None:
    await state.reset_state(with_data=False)

    # check connection
    conn_msg, access = await check_connection()
    if not access:
        await msg.answer(conn_msg)
        return

    await msg.answer("Select date:", reply_markup=await DialogCalendar().start_calendar())


async def __process_calendar(callback_query: CallbackQuery,
                             callback_data: CallbackData) -> None:
    _selected, _date = await DialogCalendar().process_selection(callback_query, callback_data)
    if _selected:
        selected_date: date = _date.date()
        await callback_query.message.edit_text("Selected date: " + selected_date.strftime('%d-%m-%y'))

        # loading...
        LOADING_MSG = "*Loading...*"
        wrapp_msg = await callback_query.message.edit_text(show_selected_wrapper(LOADING_MSG, selected_date))

        # check connection
        conn_msg, access = await check_connection()
        if not access:
            await wrapp_msg.edit_text(conn_msg)
            return

        # find homeworks
        show_list: list[Homework] = get_last_by_date(selected_date)
        if show_list == None:
            await wrapp_msg.edit_text(show_selected_wrapper(HOMEWORKS_NOT_FOUND, selected_date))
            return

        # print results
        await __template_show(wrapp_msg, show_list, selected_date=selected_date)


async def __show_page(msg: Message, page: int = 1, limit: int = 5):
    # loading...
    LOADING_MSG = "*Loading...*"
    wrapp_msg = await msg.answer(LOADING_MSG)

    # find homeworks
    show_list: list[Homework] = to_homework(
        homeworks(limit=limit, offset=(page - 1) * limit))
    if show_list == None:
        await wrapp_msg.edit_text(HOMEWORKS_NOT_FOUND)
        return

    # print results
    first_homework = show_list[0]
    count_attachments = count.attachments(first_homework.id)
    if first_homework.updatedAt != first_homework.createdAt:
        await wrapp_msg.edit_text(
            show_updated_wrapper(
                first_homework.print(count_attachments=count_attachments),
                first_homework.updatedAt
            ),
            reply_markup=list_actions_ikb(first_homework.id)
        )
    else:
        await wrapp_msg.edit_text(
            show_add_wrapper(
                first_homework.print(count_attachments=count_attachments),
                first_homework.createdAt
            ),
            reply_markup=list_actions_ikb(first_homework.id)
        )

    # print array
    for i in range(1, len(show_list)):
        count_attachments = count.attachments(show_list[i].id)
        if show_list[i].updatedAt != show_list[i].createdAt:
            await wrapp_msg.answer(
                show_updated_wrapper(
                    show_list[i].print(count_attachments=count_attachments),
                    show_list[i].updatedAt
                ),
                reply_markup=list_actions_ikb(show_list[i].id)
            )
        else:
            await wrapp_msg.answer(
                show_add_wrapper(
                    show_list[i].print(count_attachments=count_attachments),
                    show_list[i].createdAt
                ),
                reply_markup=list_actions_ikb(show_list[i].id)
            )


async def __infinity_list(msg: Message, state: FSMContext) -> None:
    await state.reset_state(with_data=False)

    page = 1
    limit = 2

    # check connection
    conn_msg, access = await check_connection()
    if not access:
        await msg.answer(conn_msg)
        return

    # page
    await __show_page(msg, page, limit)

    # load more
    if count.homeworks() > limit * page:
        await msg.answer("Load more?", reply_markup=gen_load_more(page + 1))


async def __process_infinity_list(callback_query: CallbackQuery, callback_data: CallbackData) -> None:
    page = int(callback_data["page"])
    limit = 2

    # check connection
    conn_msg, access = await check_connection()
    if not access:
        await callback_query.message.answer(conn_msg)
        return

    # show page counter
    await callback_query.message.edit_text(f"Page: {page}")

    # page
    await __show_page(callback_query.message, page, limit)

    # load more
    if count.homeworks() > limit * page:
        await callback_query.message.answer("Load more?", reply_markup=gen_load_more(page + 1))


async def __process_list_actions(callback_query: CallbackQuery, callback_data: CallbackData) -> None:
    homework_id = callback_data["id"]
    action = callback_data["act"]
    if action == "DELETE":
        delete.homework_by_id(homework_id)
        await callback_query.message.delete()
    elif action == "SHOW":
        homeworks: list[Homework] = to_homework(
            select.homework_by_id(homework_id))
        if homeworks != None:
            homeworks[0].attachments = to_attachment(
                select.homework_files(homework_id=homework_id))
            await __template_show(callback_query.message, homeworks[0])


def register_supergroup_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(
        __tomorrow, commands=['tomorrow'], state="*")

    dp.register_message_handler(
        __last_by_teacher, commands=['lastbyteacher'], state="*")

    dp.register_message_handler(
        __another_date, commands=['anotherdate'], state="*")

    dp.register_message_handler(
        __infinity_list, IsPrivate(), commands=['hws'], state="*")

    # callbacks

    dp.register_callback_query_handler(
        __process_calendar, dialog_cal_callback.filter())

    dp.register_callback_query_handler(
        __process_infinity_list, infinity_list_callback.filter(), state="*")

    dp.register_callback_query_handler(
        __process_list_actions, list_actions_hw_callback.filter(), state="*")
