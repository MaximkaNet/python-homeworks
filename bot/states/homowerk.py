from aiogram.dispatcher.filters.state import StatesGroup, State


class Homework(StatesGroup):
    workspace = State()
    show = State()
    show_last = State()

    homework = State()
    teacher = State()  # select a teacher
    teacher_empty_hw = State()
    work = State()  # add homework
    attachments = State()
    count_attachments = State()
    added_date = State()
    edit = State()
    edit_question = State()
