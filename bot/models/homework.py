from bot import models
from bot.utils.env import Config
import bot.database.methods.update as update
import bot.database.methods.select as select
import bot.database.methods.delete as delete
import bot.database.methods.insert as insert

from datetime import date
import json


class Homework:
    def __init__(self, _date: date = None, _update: date = None, _author: str = "", _tasks: list = [], _attachments: list | None = None) -> None:
        self.date: date = _date
        self.update_date: date = _date if _update == None else _update
        self.author: str = _author
        self.tasks: list[models.Task] = _tasks
        self.attachments: list = _attachments

    def update(self, tasks: list = None) -> None:
        if tasks != None:
            self.tasks = tasks
        self.update_date = date.today()
        update.homework_by(self.author, self.date, self.update_date)
        homework_id = select.homework_id(self.author, self.date)
        delete.tasks_by(homework_id)
        for task in self.tasks:
            insert.task(task.source, json.dumps(
                task.exercises), json.dumps(task.sentences), homework_id)

    def add_attachment(self, name: str, blob, type: str = "photo") -> None:
        homework_id = select.homework_id(self.author, self.date)
        insert.homework_file(name, blob, type, homework_id)

    def delete_attachment(self, name: str = "", date: date = None):
        if name != "" and date != None:
            delete.attchments(select.homework_id(name, date))
        else:
            delete.attchments(select.homework_id(self.author, self.date))

    def create(self, author: str) -> None:
        self.date = date.today()
        self.update_date = date.today()
        self.author = author
        homework_id = insert.homework(
            self.date, self.update_date, select.teacher_id(self.author))
        for task in self.tasks:
            insert.task(task.source, json.dumps(
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
            if not models.Task.validate_message(task_str):
                return False
        # parse strings
        self.tasks = []
        for string in task_input:
            temp = models.Task()
            temp.string_parser(string)
            self.tasks.append(temp)
            temp = None
        return True

    def print(self, separator: str = "|-") -> str:
        sections: str = ""
        for task in self.tasks:
            sections += task.print(separator)
        return f'*{self.author}*\n{sections}\n\n_Added: {self.date.strftime(Config.DATE_FORMAT)} ({self.date.strftime("%A")})_' if self.date == self.update_date else f'*{self.author}*\n{sections}\n\n_Updated: {self.update_date.strftime(Config.DATE_FORMAT)} ({self.date.strftime("%A")})_'
