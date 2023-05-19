from ..engine.query import select
from ..config.format import DATE_FORMAT

from datetime import date

from ..engine.exception import DBException, ConnectionError
import logging

from ..helpers.to_dict import to_dict


def teachers() -> list[dict] | None:
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
        rows = select(sql)
        schema = ['id', 'name', 'surname', 'position', 'day']
        res = to_dict(tuples=rows, schema=schema)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res


def teacher_by_id(id: int) -> list[dict] | None:
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
        rows = select(sql)
        schema = ['id', 'name', 'surname', 'position', 'day']
        res = to_dict(tuples=rows, schema=schema)
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


def homeworks(limit: int = 10, offset: int = 0) -> list[dict] | None:
    """
    Return: [
        {
            `id`,
            `created_at`,
            `updated_at`,
            `teacher_id`,
            `teacher_name`,
            `teacher_surname`,
            `teacher_position`
        }
    ]
    """

    sql = """
    SELECT
        `homeworks`.`id`,
        `homeworks`.`created_at`,
        `homeworks`.`updated_at`,
        `teachers`.`id`,
        `teachers`.`name`,
        `teachers`.`surname`,
        `teachers`.`position`
    FROM `homeworks` INNER JOIN `teachers`
        ON `homeworks`.`teacher_id` = `teachers`.`id`
    ORDER BY `homeworks`.`created_at` DESC
    LIMIT %s
    OFFSET %s
    """
    val = (limit, offset)
    try:
        rows = select(sql, val)
        schema = [
            'id', 'created_at', 'updated_at',
            'teacher_id', 'teacher_name',
            'teacher_surname', 'teacher_position']
        res = to_dict(tuples=rows, schema=schema)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res


def homework_last_by(teacher_id: str, date: date, limit: int = 1) -> list[dict] | None:
    """
    Return: [
        {
            `id`,
            `created_at`,
            `updated_at`,
            `teacher_id`,
            `teacher_name`,
            `teacher_surname`,
            `teacher_position`
        }
    ]
    """

    sql = """
    SELECT
        `homeworks`.`id`,
        `homeworks`.`created_at`,
        `homeworks`.`updated_at`,
        `teachers`.`id`,
        `teachers`.`name`,
        `teachers`.`surname`,
        `teachers`.`position`
    FROM `homeworks` INNER JOIN `teachers`
        ON `homeworks`.`teacher_id` = `teachers`.`id`
    WHERE `teachers`.`id` = %s AND `homeworks`.`created_at` < %s
    ORDER BY `homeworks`.`id` DESC
    LIMIT %s
    """
    val = (teacher_id, date.strftime(DATE_FORMAT), limit)
    try:
        rows = select(sql, val)
        schema = [
            'id', 'created_at', 'updated_at',
            'teacher_id', 'teacher_name',
            'teacher_surname', 'teacher_position']
        res = to_dict(tuples=rows, schema=schema)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res


def homework_by(teacher_id: str, date: date) -> list[dict] | None:
    """
    Return: [
        {
            `id`,
            `created_at`,
            `updated_at`,
            `teacher_id`,
            `teacher_name`,
            `teacher_surname`,
            `teacher_position`
        }
    ]
    """

    sql = """
    SELECT
        `homeworks`.`id`,
        `homeworks`.`created_at`,
        `homeworks`.`updated_at`,
        `teachers`.`id`,
        `teachers`.`name`,
        `teachers`.`surname`,
        `teachers`.`position`
    FROM `homeworks` INNER JOIN `teachers`
        ON `homeworks`.`teacher_id` = `teachers`.`id`
    WHERE `teacher_id` = %s AND `created_at` = %s
    """

    val = (teacher_id, date.strftime(DATE_FORMAT))
    try:
        rows = select(sql, val)
        schema = [
            'id', 'created_at', 'updated_at',
            'teacher_id', 'teacher_name',
            'teacher_surname', 'teacher_position']
        res = to_dict(tuples=rows, schema=schema)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res


def homework_by_id(id: int) -> list[dict] | None:
    """
    Return: [
        {
            `id`,
            `created_at`,
            `updated_at`,
            `teacher_id`,
            `teacher_name`,
            `teacher_surname`,
            `teacher_position`
        }
    ]
    """

    sql = f"""
    SELECT
        `homeworks`.`id`,
        `homeworks`.`created_at`,
        `homeworks`.`updated_at`,
        `teachers`.`id`,
        `teachers`.`name`,
        `teachers`.`surname`,
        `teachers`.`position`
    FROM `homeworks` INNER JOIN `teachers`
        ON `homeworks`.`teacher_id` = `teachers`.`id`
    WHERE `homeworks`.`id` = {id}
    """

    try:
        rows = select(sql)
        schema = [
            'id', 'created_at', 'updated_at',
            'teacher_id', 'teacher_name',
            'teacher_surname', 'teacher_position']
        res = to_dict(tuples=rows, schema=schema)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res


def homework_files(homework_id: int) -> list[dict] | None:
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
    WHERE `homework_id` = {homework_id}
    """
    try:
        rows = select(sql)
        schema = [
            'id', 'file_name', 'file_type',
            'file_blob']
        res = to_dict(tuples=rows, schema=schema)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.critical(err)
        return None
    else:
        return res


def tasks(homework_id: int) -> list[dict] | None:
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
        rows = select(sql)
        schema = ['source', 'exercises', 'sentences']
        res = to_dict(tuples=rows, schema=schema)
    except ConnectionError as err:
        logging.critical(err)
        return None
    except DBException as err:
        logging.error(err)
        return None
    else:
        return res
