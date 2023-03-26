from bot.database.engine.query import select
from bot.database.engine.config import DATE_FORMAT

from datetime import date

from bot.database.engine.exception import DBException, ConnectionError
import logging


def teachers() -> list:
    sql = "SELECT `teachers`.`name`, `teachers_work_days`.`day` FROM `teachers` INNER JOIN `teachers_work_days` ON `teachers`.`id`=`teachers_work_days`.`teacher_id` ORDER BY `teachers`.`name` ASC"
    try:
        res = select(sql)
    except ConnectionError as err:
        logging.critical(err)
        return []
    except DBException as err:
        logging.error(err)
        return []
    else:
        return res


def teacher_by(name: str) -> list:
    sql = f"SELECT `teachers`.`name`, `teachers_work_days`.`day` FROM `teachers` INNER JOIN `teachers_work_days` ON `teachers`.`id`=`teachers_work_days`.`teacher_id` WHERE `teachers`.`name` = '{name}'"
    try:
        res = select(sql)
    except ConnectionError as err:
        logging.critical(err)
        return []
    except DBException as err:
        logging.error(err)
        return []
    else:
        return res


def teacher_id(name: str) -> list:
    sql = f"SELECT `id` FROM `teachers` WHERE `name` = '{name}'"
    try:
        res = select(sql)[0][0]
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)
    else:
        return res


def homeworks(limit: int = 10, offset: int = 0, author: str = "") -> list:
    if author != "":
        sql = "SELECT homeworks.id, homeworks.date, homeworks.update, teachers.name FROM homeworks INNER JOIN teachers ON homeworks.author_id=teachers.id WHERE `teachers`.`name` = %s ORDER BY homeworks.date DESC LIMIT %s OFFSET %s"
        val = (author, limit, offset)
    else:
        sql = "SELECT homeworks.id, homeworks.date, homeworks.update, teachers.name FROM homeworks INNER JOIN teachers ON homeworks.author_id=teachers.id ORDER BY homeworks.date DESC LIMIT %s OFFSET %s"
        val = (limit, offset)
    try:
        res = select(sql, val)
    except ConnectionError as err:
        logging.critical(err)
        return []
    except DBException as err:
        logging.error(err)
        return []
    else:
        return res


def homework_last_by(author: str, date: date, limit: int = 10) -> list:
    sql = "SELECT `homeworks`.`id`,`homeworks`.`date`, `homeworks`.`update`, `teachers`.`name` FROM `homeworks` INNER JOIN `teachers` ON `homeworks`.`author_id`=`teachers`.`id` WHERE `teachers`.`name` = %s AND `homeworks`.`date` < %s ORDER BY `homeworks`.`id` DESC LIMIT %s"
    val = (author, date.strftime(DATE_FORMAT), limit)
    try:
        res = select(sql, val)
    except ConnectionError as err:
        logging.critical(err)
        return []
    except DBException as err:
        logging.error(err)
        return []
    else:
        return res


def homework_by(author: str, date: date) -> list:
    sql = "SELECT `homeworks`.`id`,`homeworks`.`date`, `homeworks`.`update`, `teachers`.`name` FROM `homeworks` INNER JOIN `teachers` ON `homeworks`.`author_id`=`teachers`.`id` WHERE `teachers`.`name` = %s AND `homeworks`.`date` = %s"
    val = (author, date.strftime(DATE_FORMAT))
    try:
        res = select(sql, val)
    except ConnectionError as err:
        logging.critical(err)
        return []
    except DBException as err:
        logging.error(err)
        return []
    else:
        return res


def homework_id(author: str, date: date) -> int:
    sql = "SELECT `homeworks`.`id` FROM `homeworks` INNER JOIN `teachers` ON `homeworks`.`author_id` = `teachers`.`id` WHERE `homeworks`.`date` = %s AND `teachers`.`name` = %s"
    val = (date.strftime(DATE_FORMAT), author)
    try:
        res = select(sql, val)[0][0]
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)
    else:
        return res


def tasks(homework_id: int) -> list:
    sql = f"SELECT `tasks`.`source`, `tasks`.`exercises`, `tasks`.`sentences` FROM `tasks` INNER JOIN `homeworks` ON `tasks`.`homework_id` = `homeworks`.id WHERE `tasks`.`homework_id` = {homework_id}"
    try:
        res = select(sql)
    except ConnectionError as err:
        logging.critical(err)
        return []
    except DBException as err:
        logging.error(err)
        return []
    else:
        return res
