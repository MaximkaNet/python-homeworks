from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

infinity_list_callback = CallbackData("infinity_list", "page")


def gen_load_more(page: int):
    ikb = InlineKeyboardMarkup()
    ikb.row()
    ikb.add(InlineKeyboardButton("Load more",
            callback_data=infinity_list_callback.new(page)))
    return ikb
