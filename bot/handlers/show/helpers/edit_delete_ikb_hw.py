from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

list_actions_hw_callback = CallbackData("list_actions_hw", "act", "id")


def list_actions_ikb(id: int) -> InlineKeyboardMarkup:
    ikb = InlineKeyboardMarkup(row_width=2)
    ikb.row()
    ikb.insert(InlineKeyboardButton(
        "Show",
        callback_data=list_actions_hw_callback.new("SHOW", id)))
    ikb.insert(InlineKeyboardButton(
        "Delete",
        callback_data=list_actions_hw_callback.new("DELETE", id)))
    return ikb
