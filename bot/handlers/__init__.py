from aiogram import Dispatcher

# from .teacher import register_supergroup_handlers
from .main import register_main_handlers
from .add import register_add_teacher_handlers, register_add_homework_handlers
from .show import register_show_teacher_handlers, register_supergroup_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_main_handlers,
        register_add_teacher_handlers,
        register_add_homework_handlers,
        register_show_teacher_handlers,
        register_supergroup_handlers
    )
    for handler in handlers:
        handler(dp)
