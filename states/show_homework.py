from aiogram.dispatcher.filters.state import State, StatesGroup


class ShowHomework(StatesGroup):
    select = State()
