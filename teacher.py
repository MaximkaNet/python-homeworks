import math
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
import db
import utils


class Teacher:
    def __init__(self, name: str = "", work_days: list[int] = []):
        self.name = name
        self.work_days = work_days

    def update(self, work_days: list[int], new_name: str = ""):
        if new_name != "":
            db.update_teacher(self.name, work_days, new_name)
            self.work_days = work_days
            self.name = new_name
            return self
        db.update_teacher(self.name, work_days)

    def get_work_days(self) -> list[int]:
        return self.work_days

    def has_work_day(self, number: int) -> bool:
        return True if number in self.work_days else False

    def print(self):
        converted_week = utils.convert_week(self.work_days)
        message = f"Teacher *{self.name}* work in "
        message += ", ".join(map(str, converted_week))
        return message


choice_teacher = CallbackData("teacher", "name")


def gen_table():
    items = convert_to_list(db.select_teachers())
    if len(items) == 0:
        utils.debug(gen_table, "Items not found")
        return None
    count_cols = math.floor(math.sqrt(len(items)))
    table = InlineKeyboardMarkup()
    row = []
    for i, item in enumerate(items):
        if i % count_cols == 0:
            table.add(*row)
            row = []
        button = InlineKeyboardButton(
            f"{item.name}", callback_data=choice_teacher.new(item.name))
        row.append(button)
    if len(row) != 0:
        table.add(*row)
    return table


def convert_to_list(tuples: list[tuple]) -> list[Teacher]:
    if len(tuples) == 0:
        return []
    teachers: list[Teacher] = []
    current_name = ""
    for item in tuples:
        if item[0] == current_name:
            teachers[-1].work_days.append(item[1])
        else:
            current_name = item[0]
            teachers.append(Teacher(item[0], [item[1]]))
    return teachers
