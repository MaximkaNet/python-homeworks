from bot.database.engine.query import delete, insert, update
from bot.database.engine.config import DATE_FORMAT
from .select import teacher_id

from datetime import date

from bot.database.engine.exception import ConnectionError, DBException
import logging


def teacher(name: str, work_days: list[int] = [], new_name: str = "") -> None:
    if new_name != "" and not len(work_days):
        sql = "UPDATE `teachers` SET `name` = %s WHERE `name` = %s"
        val = (new_name, name)
        try:
            update(sql, val)
        except ConnectionError as err:
            logging.critical(err)
        except DBException as err:
            logging.error(err)
        else:
            return
    try:
        if new_name != "":
            sql = "UPDATE `teachers` SET `name` = %s WHERE `name` = %s"
            val = (new_name, name)
            update(sql, val)
            name = new_name
        updated_id = teacher_id(name)
        sql = f"DELETE FROM `teachers_work_days` WHERE `teacher_id` = {updated_id}"
        delete(sql)
        val = []
        for day in work_days:
            val.append((updated_id, day))
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
