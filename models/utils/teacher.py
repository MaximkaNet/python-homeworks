from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

import math
import logging

from database.methods.select import teachers

from .. import Teacher

choice_teacher_callback = CallbackData("ch_teacher", "id")


def to_teacher(objs: list[dict] | None) -> list[Teacher] | None:
    if objs == None:
        return None
    teachers: list[Teacher] = []

    selected_id = None
    for teacher in objs:
        id = teacher['id']
        name = teacher['name']
        surname = teacher['surname']
        position = teacher['position']
        day = teacher['day']

        if id == selected_id:
            teachers[-1].work_days.add(day)
        else:
            selected_id = id
            initial_days = set()
            initial_days.add(day)
            teachers.append(Teacher(id=id,
                                    name=name,
                                    surname=surname,
                                    position=position,
                                    work_days=initial_days))

    return teachers


def gen_table() -> InlineKeyboardMarkup:
    items = to_teacher(teachers())
    if items == None:
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
            f"{item.name}", callback_data=choice_teacher_callback.new(item.id))
        row.append(button)
    if len(row) != 0:
        table.add(*row)
    return table
