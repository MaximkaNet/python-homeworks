from ..engine.query import query
from ..engine.config import DATE_FORMAT
from .select import select
from datetime import date


class update:
    def teacher(name: str, work_days: list[int] = [], new_name: str = ""):
        if new_name != "" and not len(work_days):
            sql = "UPDATE `teachers` SET `name` = %s WHERE `name` = %s"
            val = (new_name, name)
            update(sql, val)
            return
        if new_name != "":
            sql = "UPDATE `teachers` SET `name` = %s WHERE `name` = %s"
            val = (new_name, name)
            update(sql, val)
            name = new_name
        updated_id = select.teacher_id(name)
        sql = f"DELETE FROM `teachers_work_days` WHERE `teacher_id` = {updated_id}"
        query.delete(sql)
        val = []
        for day in work_days:
            val.append((updated_id, day))
        sql = f"INSERT INTO `teachers_work_days`(`teacher_id`, `day`) VALUES (%s, %s)"
        query.insert(sql, val)

    def homework_by(author: str, date: date, update: date):
        sql = "UPDATE `homeworks` INNER JOIN teachers ON `homeworks`.`author_id`=`teachers`.`id` SET `homeworks`.`update` = %s WHERE `teachers`.`name` = %s AND `homeworks`.`date` = %s"
        val = (update.strftime(DATE_FORMAT),
               author, date.strftime(DATE_FORMAT))
        return update(sql, val)
