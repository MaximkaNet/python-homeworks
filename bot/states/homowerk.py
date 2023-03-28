from aiogram.dispatcher.filters.state import StatesGroup, State


class Homework(StatesGroup):
    workspace = State()
    show = State()
    show_last = State()

    homework = State()
    teacher = State()  # select a teacher
    work = State()  # add homework
    added_date = State()
    edit = State()
    edit_question = State()
