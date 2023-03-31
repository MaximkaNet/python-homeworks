from bot import models
from bot.utils.env import Config
from bot.models.utils import task, teacher
import bot.database.methods.count as count
import bot.database.methods.select as select
from bot.utils.get import get_file_path, get_file

from aiogram.types import Message, InputFile, InputMediaPhoto
import logging
from datetime import date
from io import BytesIO


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


def get_by(name: str, date: date) -> models.Homework:
    homeworks = convert_to_list(
        select.homework_by(name, date))
    if len(homeworks) == 0:
        return False
    return homeworks[0]


async def save_file(msg: Message, homework: models.Homework) -> None:
    # find and save files
    file_id = None
    file_type = "document"
    if len(msg.photo) != 0:
        file_id = msg.photo[-1].file_id
        file_type = "photo"
    elif msg.document != None:
        file_id = msg.document.file_id
        file_type = "document"
    if msg.animation != None:
        file_id = msg.animation.file_id
        file_type = "animation"
    # add into state attach files
    file_path = await get_file_path(Config.TOKEN, file_id)
    name, extension, blob = await get_file(Config.TOKEN, file_path=file_path)
    homework.add_attachment(f"{name}.{extension}", blob, file_type)


def get_files(homework_id: int) -> list:
    selected_files = select.homework_files(homework_id)
    files = []
    photos = []
    animations = []
    for row in selected_files:
        if row[2] == "photo":
            photos.append(InputMediaPhoto(InputFile(BytesIO(row[1]), row[0])))
        elif row[2] == "animation":
            animations.append(InputFile(row[1], row[0]))
        else:
            files.append(InputFile(row[1], row[0]))
    return (photos, files, animations)
