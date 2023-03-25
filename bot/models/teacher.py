import bot.database.methods.update as update
from bot.utils import convert_week


class Teacher:
    def __init__(self, name: str = "", work_days: list[int] = []):
        self.name = name
        self.work_days = work_days

    def update(self, work_days: list[int], new_name: str = ""):
        if new_name != "":
            update.teacher(self.name, work_days, new_name)
            self.work_days = work_days
            self.name = new_name
            return self
        update.teacher(self.name, work_days)

    def get_work_days(self) -> list[int]:
        return self.work_days

    def has_work_day(self, number: int) -> bool:
        return True if number in self.work_days else False

    def print(self):
        converted_week = convert_week(self.work_days)
        message = f"Teacher *{self.name}* work in "
        message += ", ".join(map(str, converted_week))
        return message
