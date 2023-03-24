from bot.database.engine.query import delete
from bot.database.engine.config import DATE_FORMAT

from datetime import date


def teacher(name: str):
    sql = f"DELETE FROM teachers WHERE name = '{name}'"
    delete(sql)


def homework(date: date, author: str):
    sql = "DELETE FROM homeworks WHERE date = %s AND author_id = (SELECT `id` FROM `teachers` WHERE `name` = %s)"
    val = (date.strftime(DATE_FORMAT), author)
    delete(sql, val)


def tasks_by(homework_id: int):
    sql = f"DELETE FROM `tasks` WHERE `homework_id` = {homework_id}"
    delete(sql)
