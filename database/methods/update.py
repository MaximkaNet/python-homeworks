from ..engine.query import delete, insert, update
from ..engine.exception import ConnectionError, DBException

from ..config.format import DATE_FORMAT

from datetime import date

import logging


def teacher_name(teacher_id: int, name: str) -> None:
    sql = "UPDATE `teachers` SET `name` = %s WHERE `id` = %s"
    val = (name, teacher_id)
    try:
        update(sql, val)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)


def teacher_work_days(teacher_id: int, work_days: set[int]) -> None:
    try:
        sql = f"DELETE FROM `teachers_work_days` WHERE `teacher_id` = {teacher_id}"
        delete(sql)

        val = [(teacher_id, day) for day in work_days]
        sql = f"INSERT INTO `teachers_work_days`(`teacher_id`, `day`) VALUES (%s, %s)"
        insert(sql, val)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)


def homework_by(_author: str, _date: date, _update: date) -> None:
    sql = "UPDATE `homeworks` INNER JOIN teachers ON `homeworks`.`author_id`=`teachers`.`id` SET `homeworks`.`update` = %s WHERE `teachers`.`name` = %s AND `homeworks`.`date` = %s"
    val = (_update.strftime(DATE_FORMAT),
           _author, _date.strftime(DATE_FORMAT))
    try:
        update(sql, val)
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)
