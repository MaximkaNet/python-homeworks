from aiogram.dispatcher.filters.state import StatesGroup, State


class Teacher(StatesGroup):
    workspace = State()
    name = State()
    change_name = State()
    choice = State()
    work_days = State()
