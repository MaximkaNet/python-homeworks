from utils.converters import convert_week

from database.methods import update
from database.methods import insert
from database.methods import delete


class Teacher:
    def __init__(
        self,
        id: int,
        name: str = "",
        surname: str = "",
        position: str = "",
        work_days: set[int] = set()
    ) -> None:
        self.id = id
        self.name = name
        self.surname = surname
        self.position = position
        self.work_days = work_days

    def __str__(self) -> str:
        res = ""
        res += self.position if self.position != None else ""
        res += self.name
        res += self.surname if self.surname != None else ""
        return res

    def create(self) -> None:
        insert.teacher(name=self.name,
                       surname=self.surname if self.surname != "" else None,
                       position=self.position if self.position != "" else None,
                       work_days=self.work_days)

    def change_name(self, new_name: str) -> None:
        update.teacher_name(teacher_id=self.id, name=new_name)

    def change_work_days(self, new_work_days: set[int]) -> None:
        update.teacher_work_days(teacher_id=self.id, work_days=new_work_days)

    def delete(self) -> None:
        delete.teacher_by_id(self.id)

    def has_work_day(
        self,
        number: int
    ) -> bool:
        return True if number in self.work_days else False

    def print(self) -> str:
        converted_week = convert_week(self.work_days)
        message = f"*{self.name}* work in " + \
            ", ".join(converted_week)
        return message
