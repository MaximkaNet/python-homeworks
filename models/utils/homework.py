from aiogram.types import Message
from models import Homework, Attachment, Teacher
from models.utils import task, teacher

from utils.get import get_file_path, get_file

import database.methods.count as count
import database.methods.select as select

import logging
from datetime import date
from config.bot import BotConfig

from uuid import uuid4

from models.utils import attachment


def to_homework(objs: list[dict] | None) -> list[Homework] | None:
    if objs == None:
        return None

    homeworks: list[Homework] = []
    for homework in objs:
        tasks = task.to_task(select.tasks(homework['id']))

        homeworks.append(Homework(
            id=homework['id'],
            createdAt=homework['created_at'],
            updatedAt=homework['updated_at'],
            teacher=Teacher(
                id=homework['teacher_id'],
                name=homework['teacher_name'],
                surname=homework['teacher_surname'],
                position=homework['teacher_position']),
            tasks=tasks))

    return homeworks


def get_last_by_date(date: date) -> list[Homework]:
    day = date.weekday()
    # get teachers
    teachers = count.teachers()
    homeworks = count.homeworks()
    if teachers == 0:
        logging.debug("Teachers not found.")
        return None
    elif homeworks == 0:
        logging.debug("Homeworks not found.")
        return None
    # find candidates
    teachers = teacher.to_teacher(select.teachers())
    if teachers == None:
        logging.debug("Teachers not found.")
        return
    candidates = []
    for _teacher in teachers:
        if _teacher.has_work_day(day):
            candidates.append(_teacher)
    if len(candidates) == 0:
        logging.debug("Candidates is not found.")
        return None
    # get homeworks
    homeworks = []
    show_list: list[Homework] = []
    for candidate in candidates:
        homeworks = to_homework(
            select.homework_last_by(candidate.id, date))
        if homeworks != None:
            for homework in homeworks:
                if homework not in show_list:
                    homework.attachments = attachment.to_attachment(
                        select.homework_files(homework.id))
                    show_list.append(homework)
                    break

    if show_list == None:
        logging.debug(
            f"Homeworks for {date.strftime('%Y-%m-%d')} is not found")
        return None

    return show_list if len(show_list) > 0 else None


# def get_by(name: str, date: date) -> Homework:
#     homeworks = to_homework(
#         select.homework_by(name, date))
#     if len(homeworks) == 0:
#         return False
#     return homeworks[0]
