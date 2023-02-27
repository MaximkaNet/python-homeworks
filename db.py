from mysql.connector import connect
from mysql.connector import Error
from datetime import date
import utils
import config

DATE_FORMAT = "%Y-%m-%d"


def connection():
    try:
        cn = connect(username=config.USERNAME, password=config.PASSWORD,
                     host=config.HOST, database=config.DATABASE)
    except Error as err:
        utils.debug(connection, "Connection error: ", err)
    finally:
        return cn


def query_insert(sql: str, val: tuple | list[tuple] = None):
    try:
        con = connection()
        cursor = con.cursor()
        if isinstance(val, tuple):
            cursor.execute(sql, val)
            con.commit()
            return cursor.lastrowid
        cursor.executemany(sql, val)
        con.commit()
        return cursor.lastrowid
    except Error as err:
        utils.debug(query_insert, err)


def query_select(sql: str, val: tuple = None):
    try:
        con = connection()
        cursor = con.cursor()
        cursor.execute(sql, val)
        records = cursor.fetchall()
        return records
    except Error as err:
        utils.debug(query_select, err)


def query_update(sql: str, val: tuple = None):
    try:
        con = connection()
        cursor = con.cursor()
        cursor.execute(sql, val)
        con.commit()
    except Error as err:
        utils.debug(query_update, err)


def query_delete(sql: str, val: tuple = None):
    try:
        con = connection()
        cursor = con.cursor()
        cursor.execute(sql, val)
        con.commit()
    except Error as err:
        utils.debug(query_delete, err)


def query_aggregate(sql, val: tuple = None):
    try:
        con = connection()
        cursor = con.cursor()
        cursor.execute(sql, val)
        return cursor.fetchall()
    except Error as err:
        utils.debug(query_aggregate, err)


def select_teachers():
    sql = "SELECT `teachers`.`name`, `teachers_work_days`.`day` FROM `teachers` INNER JOIN `teachers_work_days` ON `teachers`.`id`=`teachers_work_days`.`teacher_id` ORDER BY `teachers`.`name` ASC"
    return query_select(sql)


def select_teacher_id(name: str):
    sql = f"SELECT `id` FROM `teachers` WHERE `name` = '{name}'"
    return query_select(sql)[0][0]


def insert_teacher(name: str, work_days: list[int]):
    sql = f"INSERT INTO `teachers`(`name`) VALUE '{name}'"
    lastrowid = query_insert(sql)
    sql = "INSERT INTO `teachers_work_days`(`teacher_id`, `day`) VALUES (%s, %s)"
    val = [(lastrowid, item) for item in work_days]
    query_insert(sql, val)


def update_teacher(name: str, work_days: list[int], new_name: str = ""):
    if new_name != "":
        sql = f"UPDATE `teachers`(`name`) SET `name` = '{new_name}'"
        query_update(sql)
        name = new_name
    updated_id = select_teacher_id(name)
    sql = f"DELETE FROM `teachers_work_days` WHERE `teacher_id` = {updated_id}"
    query_delete(sql)
    val = []
    for day in work_days:
        val.append((updated_id, day))
    sql = f"INSERT INTO `teachers_work_days`(`teacher_id`, `day`) VALUES (%s, %s)"
    query_insert(sql, val)


def delete_teacher(name: str):
    sql = f"DELETE FROM teachers WHERE name = '{name}'"
    query_delete(sql)


def count_teachers():
    sql = "SELECT COUNT(*) FROM `teachers`"
    return query_aggregate(sql)[0][0]


def select_homeworks(limit: int = 30, offset: int = 0):
    sql = "SELECT homeworks.id, homeworks.date, homeworks.update, teachers.name FROM homeworks INNER JOIN teachers ON homeworks.author_id=teachers.id ORDER BY homeworks.date DESC LIMIT %s OFFSET %s"
    val = (limit, offset)
    return query_select(sql, val)


def select_last_homework_by(author: str, date: date, limit: int = 20):
    sql = "SELECT `homeworks`.`id`,`homeworks`.`date`, `homeworks`.`update`, `teachers`.`name` FROM `homeworks` INNER JOIN `teachers` ON `homeworks`.`author_id`=`teachers`.`id` WHERE `teachers`.`name` = %s AND `homeworks`.`date` <= %s LIMIT %s"
    val = (author, date.strftime(DATE_FORMAT), limit)
    return query_select(sql, val)


def select_homework_by(author: str, date: date):
    sql = "SELECT `homeworks`.`id`,`homeworks`.`date`, `homeworks`.`update`, `teachers`.`name` FROM `homeworks` INNER JOIN `teachers` ON `homeworks`.`author_id`=`teachers`.`id` WHERE `teachers`.`name` = %s AND `homeworks`.`date` = %s"
    val = (author, date.strftime(DATE_FORMAT))
    return query_select(sql, val)


def select_homework_id(author: str, date: date):
    sql = "SELECT `homeworks`.`id` FROM `homeworks` INNER JOIN `teachers` ON `homeworks`.`author_id` = `teachers`.`id` WHERE `homeworks`.`date` = %s AND `teachers`.`name` = %s"
    val = (date.strftime(DATE_FORMAT), author)
    return query_select(sql, val)[0][0]


def insert_homework(date: date, update: date, author_id: int):
    sql = "INSERT INTO `homeworks`(`date`, `update`, `author_id`) VALUES (%s, %s, %s)"
    val = (date.strftime(DATE_FORMAT), update.strftime(DATE_FORMAT), author_id)
    return query_insert(sql, val)


def update_homework_by(author: str, date: date, update: date):
    sql = "UPDATE `homeworks` INNER JOIN teachers ON `homeworks`.`author_id`=`teachers`.`id` SET `homeworks`.`update` = %s WHERE `teachers`.`name` = %s AND `homeworks`.`date` = %s"
    val = (update.strftime(DATE_FORMAT), author, date.strftime(DATE_FORMAT))
    return query_update(sql, val)


def delete_homework(date: date, author: str):
    sql = "DELETE FROM homeworks WHERE date = %s AND author_id = (SELECT `id` FROM `teachers` WHERE `name` = %s)"
    val = (date.strftime(DATE_FORMAT), author)
    query_delete(sql, val)


def count_homeworks():
    sql = "SELECT COUNT(*) FROM `homeworks`"
    return query_aggregate(sql)[0][0]


def select_tasks(hw_id: int):
    sql = f"SELECT `tasks`.`source`, `tasks`.`exercises`, `tasks`.`sentences` FROM `tasks` INNER JOIN `homeworks` ON `tasks`.`homework_id` = `homeworks`.id WHERE `tasks`.`homework_id` = {hw_id}"
    return query_select(sql)


def insert_task(source: str, exercises: str, sentences: str, homework_id: int):
    sql = "INSERT INTO `tasks`(`source`, `exercises`, `sentences`, `homework_id`) VALUES (%s, %s, %s, %s)"
    val = (source, exercises, sentences, homework_id)
    return query_insert(sql, val)


def delete_tasks_by(homework_id: int):
    sql = f"DELETE FROM `tasks` WHERE `homework_id` = {homework_id}"
    query_delete(sql)
