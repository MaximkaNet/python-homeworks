from bot import models
from bot.models.utils import task, teacher
from bot.utils.env import Config
from bot.database.methods import count, select

import logging
from datetime import date


def convert_to_list(tuples: list[tuple]) -> list[models.Homework]:
    if len(tuples) == 0:
        return []
    homeworks: list[models.Homework] = []
    for item in tuples:
        tasks = task.convert_to_list(select.tasks(item[0]))
        homeworks.append(models.Homework(item[1], item[2], item[3], tasks))
    return homeworks


def get_last_by_date(date: date) -> list[models.Homework]:
    day = date.weekday()
    # get teachers
    teachers = count.teachers()
    homeworks = count.homeworks()
    if teachers == 0:
        logging.debug("Teachers not found.")
        return []
    elif homeworks == 0:
        logging.debug("Homeworks not found.")
        return []
    # find candidates
    teachers = teacher.convert_to_list(select.teachers())
    candidates = []
    for _teacher in teachers:
        if _teacher.has_work_day(day):
            candidates.append(_teacher.name)
    if len(candidates) == 0:
        logging.debug("Candidates is not found.")
        return []
    # get homeworks
    homeworks = count.homeworks()
    show_list = []
    for candidate in candidates:
        homeworks = convert_to_list(
            select.homework_last_by(candidate, date))
        for homework in homeworks:
            if homework not in show_list:
                show_list.append(homework)
                break
    # show homeworks
    if len(show_list) == 0:
        logging.debug(
            f"Homeworks for {date.strftime(Config.DATE_FORMAT)} is not found")
        return []

    return show_list


def get_by(name: str, date: date):
    homeworks = convert_to_list(
        select.homework_by(name, date))
    if len(homeworks) == 0:
        return False
    return homeworks[0]
