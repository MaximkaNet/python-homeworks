from ..engine.query import select
from ..config.format import DATE_FORMAT

from datetime import date

from ..engine.exception import DBException, ConnectionError
import logging


def teachers() -> list:
    """
    Return: [
        {
            `id`,
            `name`,
            `surname`,
            `position`,
            `day`
        }
    ]
    """

    sql = """
    SELECT 
        `teachers`.`id`, 
        `teachers`.`name`, 
        `teachers`.`surname`, 
        `teachers`.`position`,
        `teachers_work_days`.`day`
    FROM `teachers` INNER JOIN `teachers_work_days`
        ON `teachers`.`id` = `teachers_work_days`.`teacher_id`
    ORDER BY `teachers`.`name` ASC
    """
    try:
        res = select(sql)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res


def teacher_by_id(id: int) -> list:
    """
    Return: [
        {
            `id`,
            `name`,
            `surname`,
            `position`,
            `day`
        }
    ]
    """

    sql = f"""
    SELECT 
        `teachers`.`id`, 
        `teachers`.`name`, 
        `teachers`.`surname`, 
        `teachers`.`position`,
        `teachers_work_days`.`day`
    FROM `teachers` INNER JOIN `teachers_work_days`
        ON `teachers`.`id` = `teachers_work_days`.`teacher_id`
    WHERE `teachers`.`id` = {id}
    """
    try:
        res = select(sql)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res


# def teacher_by(name: str) -> list:
#     sql = f"SELECT `teachers`.`id`, `teachers`.`name`, `teachers_work_days`.`day` FROM `teachers` INNER JOIN `teachers_work_days` ON `teachers`.`id`=`teachers_work_days`.`teacher_id` WHERE `teachers`.`name` = '{name}'"
#     try:
#         res = select(sql)
#     except ConnectionError as err:
#         logging.critical(err)
#         return []
#     except DBException as err:
#         logging.error(err)
#         return []
#     else:
#         return res


# def teacher_id(name: str) -> list:
#     sql = f"SELECT `id` FROM `teachers` WHERE `name` = '{name}'"
#     try:
#         res = select(sql)[0][0]
#     except ConnectionError as err:
#         logging.critical(err)
#     except DBException as err:
#         logging.error(err)
#     else:
#         return res


def homeworks(limit: int = 10, offset: int = 0) -> list:
    """
    Return: [
        {
            `id`,
            `created_at`,
            `updated_at`,
            `teacher_name`
        }
    ]
    """

    sql = """
    SELECT
        `homeworks`.`id`,
        `homeworks`.`created_at`,
        `homeworks`.`updated_at`,
        `teachers`.`name`
    FROM `homeworks` INNER JOIN `teachers`
        ON `homeworks`.`teacher_id` = `teachers`.`id`
    ORDER BY `homeworks`.`created_at` DESC
    LIMIT %s
    OFFSET %s
    """
    val = (limit, offset)
    try:
        res = select(sql, val)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res


def homework_last_by(teacher_id: str, date: date, limit: int = 1) -> list:
    """
    Return: [
        {
            `id`,
            `created_at`,
            `updated_at`,
            `teacher_name`
        }
    ]
    """

    sql = """
    SELECT
        `homeworks`.`id`,
        `homeworks`.`created_at`,
        `homeworks`.`updated_at`,
        `teachers`.`name`
    FROM `homeworks` INNER JOIN `teachers`
        ON `homeworks`.`teacher_id` = `teachers`.`id`
    WHERE `teachers`.`id` = %s AND `homeworks`.`created_at` < %s
    ORDER BY `homeworks`.`id` DESC
    LIMIT %s
    """
    val = (teacher_id, date.strftime(DATE_FORMAT), limit)
    try:
        res = select(sql, val)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res


def homework_by(teacher_id: str, date: date) -> list:
    """
    Return: [
        {
            `id`,
            `file_name`,
            `file_type`,
            `file_blob`
        }
    ]
    """

    sql = """
    SELECT
        `homeworks`.`id`,
        `homeworks`.`created_at`,
        `homeworks`.`updated_at`,
        `teachers`.`name`
    FROM `homeworks` INNER JOIN `teachers`
        ON `homeworks`.`teacher_id` = `teachers`.`id`
    WHERE `teacher_id` = %s AND `created_at` = %s
    """

    val = (teacher_id, date.strftime(DATE_FORMAT))
    try:
        res = select(sql, val)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res


def homework_files(id: int):
    """
    Return: [
        {
            `id`,
            `file_name`,
            `file_type`,
            `file_blob`
        }
    ]
    """

    sql = f"""
    SELECT
        `id`,
        `file_name`,
        `file_type`,
        `file_blob`
    FROM `attachments`
    WHERE `homework_id` = {id}
    """
    try:
        res = select(sql)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.critical(err)
        return None
    else:
        return res


# def homework_id(author: str, date: date) -> int:
#     """
#     Return: [
#         {
#             `id`
#         }
#     ]
#     """

#     sql = """
#     SELECT
#         `homeworks`.`id`
#     FROM `homeworks` INNER JOIN `teachers`
#     ON `homeworks`.`author_id` = `teachers`.`id`
#     WHERE `homeworks`.`date` = %s AND `teachers`.`name` = %s
#     """
#     val = (date.strftime(DATE_FORMAT), author)
#     try:
#         res = select(sql, val)[0][0]
#     except ConnectionError as err:
#         logging.critical(err)
#     except DBException as err:
#         logging.error(err)
#     else:
#         return res


def tasks(homework_id: int) -> list:
    """
    Return: [
        {
            `source`,
            `exercises`,
            `sentences`
        }
    ]
    """

    sql = f"""
    SELECT
        `source`,
        `exercises`,
        `sentences`
    FROM `tasks`
    WHERE `homework_id` = {homework_id}
    """
    try:
        res = select(sql)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res
