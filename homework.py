import json
from datetime import date
from task import Task
import task
import config
import db
import teacher
from utils import debug


class Homework:
    def __init__(self, _date: date = None, _update: date = None, _author: str = "", _tasks: list = []):
        self.date: date = _date
        self.update_date: date = _date if _update == None else _update
        self.author: str = _author
        self.tasks: list[Task] = _tasks

    def update(self, tasks: list):
        self.tasks = tasks
        self.update_date = date.today()
        db.update_homework_by(self.author, self.date, self.update_date)
        homework_id = db.select_homework_id(self.author, self.date)
        db.delete_tasks_by(homework_id)
        for task in self.tasks:
            db.insert_task(task.source, json.dumps(
                task.exercises), json.dumps(task.sentences), homework_id)

    def create(self, author: str):
        self.date = date.today()
        self.update_date = date.today()
        self.author = author
        homework_id = db.insert_homework(
            self.date, self.update_date, db.select_teacher_id(self.author))
        for task in self.tasks:
            db.insert_task(task.source, json.dumps(
                task.exercises), json.dumps(task.sentences), homework_id)

    # convert task list to unparsed type

    def convert_tasks(self) -> str:
        res = ""
        for item in self.tasks:
            res += f"\n{item.convert_unparsed()}"
        return res

    def parse_message(self, message: str) -> bool:
        task_input = message.split("\n")
        # validate message
        for task_str in task_input:
            if not Task.validate_message(task_str):
                return False
        # parse strings
        self.tasks = []
        for string in task_input:
            temp = Task()
            temp.string_parser(string)
            self.tasks.append(temp)
            temp = None
        return True

    def print(self, separator: str = "|-"):
        sections: str = ""
        for task in self.tasks:
            sections += task.print(separator)
        return f'*{self.author}*\n{sections}\n\n_Added: {self.date.strftime(config.DATE_FORMAT)} ({self.date.strftime("%A")})_' if self.date == self.update_date else f'*{self.author}*\n{sections}\n\n_Updated: {self.update_date.strftime(config.DATE_FORMAT)} ({self.date.strftime("%A")})_'


def convert_to_list(tuples: list[tuple]) -> list[Homework]:
    if len(tuples) == 0:
        return []
    homeworks: list[Homework] = []
    for item in tuples:
        tasks = task.convert_to_list(db.select_tasks(item[0]))
        homeworks.append(Homework(item[1], item[2], item[3], tasks))
    return homeworks


def get_last_by_date(date: date) -> list[Homework]:
    day = date.weekday()
    # get teachers
    teachers = db.count_teachers()
    homeworks = db.count_homeworks()
    if teachers == 0:
        debug(get_last_by_date, "Teachers not found.")
        return []
    elif homeworks == 0:
        debug(get_last_by_date, "Homeworks not found.")
    # find candidates
    teachers = teacher.convert_to_list(db.select_teachers())
    candidates = []
    for _teacher in teachers:
        if _teacher.has_work_day(day):
            debug(get_last_by_date, _teacher)
            candidates.append(_teacher.name)
    if len(candidates) == 0:
        debug(get_last_by_date, "Candidates is not found.")
        return []
    # get homeworks
    homeworks = db.count_homeworks()
    show_list = []
    for candidate in candidates:
        homeworks = convert_to_list(
            db.select_last_homework_by(candidate, date))
        for homework in homeworks:
            if homework not in show_list:
                show_list.append(homework)
                break
    # show homeworks
    if len(show_list) == 0:
        debug(
            get_last_by_date, f"Homeworks for {date.strftime(config.DATE_FORMAT)} is not found")
        return []

    return show_list


def get_by(name: str, date: date):
    homeworks = convert_to_list(db.select_homework_by(name, date))
    if len(homeworks) == 0:
        return False
    return homeworks[0]
