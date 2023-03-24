from bot.database.engine.query import select
from bot.database.engine.config import DATE_FORMAT

from datetime import date


def teachers():
    sql = "SELECT `teachers`.`name`, `teachers_work_days`.`day` FROM `teachers` INNER JOIN `teachers_work_days` ON `teachers`.`id`=`teachers_work_days`.`teacher_id` ORDER BY `teachers`.`name` ASC"
    return select(sql)


def teacher_by(name: str):
    sql = f"SELECT `teachers`.`name`, `teachers_work_days`.`day` FROM `teachers` INNER JOIN `teachers_work_days` ON `teachers`.`id`=`teachers_work_days`.`teacher_id` WHERE `teachers`.`name` = '{name}'"
    return select(sql)


def teacher_id(name: str):
    sql = f"SELECT `id` FROM `teachers` WHERE `name` = '{name}'"
    return select(sql)[0][0]


def homeworks(limit: int = 10, offset: int = 0, author: str = ""):
    if author != "":
        sql = "SELECT homeworks.id, homeworks.date, homeworks.update, teachers.name FROM homeworks INNER JOIN teachers ON homeworks.author_id=teachers.id WHERE `teachers`.`name` = %s ORDER BY homeworks.date DESC LIMIT %s OFFSET %s"
        val = (author, limit, offset)
    else:
        sql = "SELECT homeworks.id, homeworks.date, homeworks.update, teachers.name FROM homeworks INNER JOIN teachers ON homeworks.author_id=teachers.id ORDER BY homeworks.date DESC LIMIT %s OFFSET %s"
        val = (limit, offset)
    return select(sql, val)


def homework_last_by(author: str, date: date, limit: int = 10):
    sql = "SELECT `homeworks`.`id`,`homeworks`.`date`, `homeworks`.`update`, `teachers`.`name` FROM `homeworks` INNER JOIN `teachers` ON `homeworks`.`author_id`=`teachers`.`id` WHERE `teachers`.`name` = %s AND `homeworks`.`date` < %s ORDER BY `homeworks`.`id` DESC LIMIT %s"
    val = (author, date.strftime(DATE_FORMAT), limit)
    return select(sql, val)


def homework_by(author: str, date: date):
    sql = "SELECT `homeworks`.`id`,`homeworks`.`date`, `homeworks`.`update`, `teachers`.`name` FROM `homeworks` INNER JOIN `teachers` ON `homeworks`.`author_id`=`teachers`.`id` WHERE `teachers`.`name` = %s AND `homeworks`.`date` = %s"
    val = (author, date.strftime(DATE_FORMAT))
    return select(sql, val)


def homework_id(author: str, date: date):
    sql = "SELECT `homeworks`.`id` FROM `homeworks` INNER JOIN `teachers` ON `homeworks`.`author_id` = `teachers`.`id` WHERE `homeworks`.`date` = %s AND `teachers`.`name` = %s"
    val = (date.strftime(DATE_FORMAT), author)
    return select(sql, val)[0][0]


def tasks(homework_id: int):
    sql = f"SELECT `tasks`.`source`, `tasks`.`exercises`, `tasks`.`sentences` FROM `tasks` INNER JOIN `homeworks` ON `tasks`.`homework_id` = `homeworks`.id WHERE `tasks`.`homework_id` = {homework_id}"
    return select(sql)
