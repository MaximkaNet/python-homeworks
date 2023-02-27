from aiogram.dispatcher.filters.state import StatesGroup, State


class Homework(StatesGroup):
    homework = State()
    teacher = State()
    work = State()
    add_date = State()
    edit = State()
    edit_question = State()
