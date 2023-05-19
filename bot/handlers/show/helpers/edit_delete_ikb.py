from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

edit_delete_callback = CallbackData("edit_delete", "act", "id")


def edit_delete_ikb(id: int) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=2)
    ikb.row()
    # ikb.insert(InlineKeyboardButton(
    #     "Edit",
    #     callback_data=edit_delete_callback.new("EDIT", id)))
    ikb.insert(InlineKeyboardButton(
        "Delete",
        callback_data=edit_delete_callback.new("DELETE", id)))
    return ikb
