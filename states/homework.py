from aiogram.dispatcher.filters.state import StatesGroup, State


class Homework(StatesGroup):
    workspace = State()
    show = State()

    homework = State()
    teacher = State()  # select a teacher
    work = State()  # add homework
    add_date = State()
    edit = State()
    edit_question = State()
