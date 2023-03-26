from bot.database.engine.query import delete
from bot.database.engine.config import DATE_FORMAT

from datetime import date

from bot.database.engine.exception import ConnectionError, DBException
import logging


def teacher(name: str) -> None:
    sql = f"DELETE FROM teachers WHERE name = '{name}'"
    try:
        delete(sql)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)


def homework(date: date, author: str) -> None:
    sql = "DELETE FROM homeworks WHERE date = %s AND author_id = (SELECT `id` FROM `teachers` WHERE `name` = %s)"
    val = (date.strftime(DATE_FORMAT), author)
    try:
        delete(sql, val)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)


def tasks_by(homework_id: int) -> None:
    sql = f"DELETE FROM `tasks` WHERE `homework_id` = {homework_id}"
    try:
        delete(sql)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)
