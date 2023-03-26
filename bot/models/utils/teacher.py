from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import models
from bot.callbacks.teacher import choice_teacher_callback
import bot.database.methods.select as select

import math
import logging


def gen_table() -> InlineKeyboardMarkup:
    items = convert_to_list(select.teachers())
    if len(items) == 0:
        logging.debug("Items not found")
        return None
    count_cols = round(math.sqrt(len(items)))
    table = InlineKeyboardMarkup()
    row = []
    for i, item in enumerate(items):
        if i % count_cols == 0:
            table.add(*row)
            row = []
        button = InlineKeyboardButton(
            f"{item.name}", callback_data=choice_teacher_callback.new(item.name))
        row.append(button)
    if len(row) != 0:
        table.add(*row)
    return table


def convert_to_list(tuples: list[tuple]) -> list[models.Teacher]:
    if len(tuples) == 0:
        return []
    teachers: list[models.Teacher] = []
    current_name = ""
    for item in tuples:
        if item[0] == current_name:
            teachers[-1].work_days.append(item[1])
        else:
            current_name = item[0]
            teachers.append(models.Teacher(item[0], [item[1]]))
    return teachers
