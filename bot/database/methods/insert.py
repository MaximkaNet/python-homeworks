from ..engine.query import query
from ..engine.config import DATE_FORMAT
from datetime import date


class insert:
    def teacher(name: str, work_days: list[int]):
        sql = f"INSERT INTO `teachers`(`name`) VALUES ('{name}')"
        lastrowid = query.insert(sql)
        sql = "INSERT INTO `teachers_work_days`(`teacher_id`, `day`) VALUES (%s, %s)"
        val = [(lastrowid, item) for item in work_days]
        query.insert(sql, val)

    def homework(date: date, update: date, author_id: int):
        sql = "INSERT INTO `homeworks`(`date`, `update`, `author_id`) VALUES (%s, %s, %s)"
        val = (date.strftime(DATE_FORMAT),
               update.strftime(DATE_FORMAT), author_id)
        return query.insert(sql, val)

    def task(source: str, exercises: str, sentences: str, homework_id: int):
        sql = "INSERT INTO `tasks`(`source`, `exercises`, `sentences`, `homework_id`) VALUES (%s, %s, %s, %s)"
        val = (source, exercises, sentences, homework_id)
        return query.insert(sql, val)
