from aiogram.dispatcher.filters.state import StatesGroup, State


class Teacher(StatesGroup):
    name = State()
    work_days = State()
