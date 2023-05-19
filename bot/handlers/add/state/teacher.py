from aiogram.dispatcher.filters.state import StatesGroup, State


class TeacherState(StatesGroup):
    name: State = State()
    select_days: State = State()
