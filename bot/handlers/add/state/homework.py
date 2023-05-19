from aiogram.dispatcher.filters.state import State, StatesGroup


class HomeworkAddState(StatesGroup):
    homework = State()
    attachments = State()
    main_msg = State()
