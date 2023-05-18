from ..engine.query import insert
from ..config.format import DATE_FORMAT

from datetime import date

from ..engine.exception import DBException, ConnectionError
import logging
from uuid import uuid4


def teacher(name: str, surname: str, position: str, work_days: list[int]) -> int:
    try:
        sql = """
        INSERT INTO `teachers`(`name`, `surname`, `position`)
        VALUES (%s, %s, %s)
        """
        val = (name, surname, position)
        lastrowid = insert(sql, val)

        sql = "INSERT INTO `teachers_work_days`(`teacher_id`, `day`) VALUES (%s, %s)"
        val = [(lastrowid, item) for item in work_days]

        res = insert(sql, val)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)
    finally:
        return res


def homework(created_at: date, updated_at: date, teacher_id: int) -> int:
    sql = "INSERT INTO `homeworks`(`created_at`, `updated_at`, `teacher_id`) VALUES (%s, %s, %s)"
    val = (created_at.strftime(DATE_FORMAT),
           updated_at.strftime(DATE_FORMAT), teacher_id)
    try:
        res = insert(sql, val)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)
    else:
        return res


def homework_file(name: str, blob: bytes, type: str, homework_id: int) -> None:
    sql = "INSERT INTO `attachments`(`id`, `file_name`, `file_blob`, `file_type`, `homework_id`) VALUES (%s, %s, %s, %s, %s)"
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
