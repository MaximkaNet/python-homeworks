from ..engine.query import query
from ..engine.config import DATE_FORMAT
from datetime import date


class delete:
    def delete_teacher(name: str):
        sql = f"DELETE FROM teachers WHERE name = '{name}'"
        query.delete(sql)

    def delete_homework(date: date, author: str):
        sql = "DELETE FROM homeworks WHERE date = %s AND author_id = (SELECT `id` FROM `teachers` WHERE `name` = %s)"
        val = (date.strftime(DATE_FORMAT), author)
        query.delete(sql, val)

    def delete_tasks_by(homework_id: int):
        sql = f"DELETE FROM `tasks` WHERE `homework_id` = {homework_id}"
        query.delete(sql)
