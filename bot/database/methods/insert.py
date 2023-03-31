from bot.database.engine.query import insert
from bot.database.engine.config import DATE_FORMAT

from datetime import date

from bot.database.engine.exception import DBException, ConnectionError
import logging
from uuid import uuid4


def teacher(name: str, work_days: list[int]) -> None:
    try:
        sql = f"INSERT INTO `teachers`(`name`) VALUES ('{name}')"
        lastrowid = insert(sql)
        sql = "INSERT INTO `teachers_work_days`(`teacher_id`, `day`) VALUES (%s, %s)"
        val = [(lastrowid, item) for item in work_days]
        insert(sql, val)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)


def homework(date: date, update: date, author_id: int) -> int:
    sql = "INSERT INTO `homeworks`(`date`, `update`, `author_id`) VALUES (%s, %s, %s)"
    val = (date.strftime(DATE_FORMAT),
           update.strftime(DATE_FORMAT), author_id)
    try:
        res = insert(sql, val)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)
    else:
        return res


def homework_file(name: str, blob: bytes, type: str, homework_id: int) -> None:
    sql = "INSERT INTO `attachments`(`id`, `name`, `file`, `file_type`, `homework_id`) VALUES (%s, %s, %s, %s, %s)"
    val = (uuid4().hex, name, blob, type, homework_id)
    try:
        res = insert(sql, val)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.critical(err)


def task(source: str, exercises: str, sentences: str, homework_id: int) -> int:
    sql = "INSERT INTO `tasks`(`source`, `exercises`, `sentences`, `homework_id`) VALUES (%s, %s, %s, %s)"
    val = (source, exercises, sentences, homework_id)
    try:
        res = insert(sql, val)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)
    else:
        return res
