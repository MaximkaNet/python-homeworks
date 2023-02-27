from aiogram.dispatcher.filters.state import State, StatesGroup


class Print(StatesGroup):
    actions = State()
    edit_obj = State()
    edit = State()
    show = State()
    teacher = State()
