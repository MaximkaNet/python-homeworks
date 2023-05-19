from .task import Task
from .attachment import Attachment
from .teacher import Teacher

from aiogram.types import Message, InputMediaPhoto, InputMedia
from uuid import uuid4

from database.methods import update
from database.methods import select
from database.methods import delete
from database.methods import insert

from utils.validator import validate_message
from utils.get import get_file_path, get_file

from datetime import date
from config.bot import AdminBotConfig


class Homework:
    def __init__(
            self,
            id: int = None,
            createdAt: date = None,
            updatedAt: date = None,
            teacher: Teacher = None,
            tasks: list[Task] = None,
            attachments: list[Attachment] = None
    ) -> None:
        self.id: int = id
        self.createdAt: date = createdAt
        self.updatedAt: date = createdAt if updatedAt == None else updatedAt
        self.teacher: Teacher = teacher
        self.tasks: list[Task] = tasks
        self.attachments: list[Attachment] = attachments

    def create(
        self,
        _date: date,
        teacher_id: int
    ) -> None:
        self.createdAt = _date
        self.updatedAt = _date
        # insert homework node
        self.id = insert.homework(
            created_at=self.createdAt,
            updated_at=self.updatedAt,
            teacher_id=teacher_id)

        # insert tasks
        for task in self.tasks:
            task.insert(self.id)

        # insert attachments
        for attachment in self.attachments:
            attachment.insert(self.id)

    async def add_attachment(
        self,
        msg: Message
    ) -> None:
        file_id = None
        file_type = "document"
        file_name = ""
        if len(msg.photo) != 0:
            file_id = msg.photo[-1].file_id
            file_type = "photo"
            file_name = uuid4().hex
        elif msg.animation != None:
            file_id = msg.animation.file_id
            file_type = "animation"
            file_name = msg.animation.file_name
        if msg.document != None:
            file_id = msg.document.file_id
            file_type = "document"
            file_name = msg.document.file_name

        file_path = await get_file_path(AdminBotConfig.TOKEN, file_id)
        blob = await get_file(AdminBotConfig.TOKEN, file_path=file_path)

        # insert
        attachment = Attachment(None, file_name, blob, file_type)
        attachment.insert(self.id)

    def print(
        self,
        separator: str = "|-",
        count_attachments: int = 0
    ) -> str:
        sections: str = ""
        for task in self.tasks:
            sections += task.print(separator)
        body = f"*{self.teacher}*\n{sections}\n"
        if count_attachments == 0:
            return body
        elif count_attachments > 0:
            attachements = f"\n📎 *Attached: {count_attachments}*"
            return body + attachements

    async def show_attachments(
        self,
        msg: Message
    ) -> None:
        if self.attachments == None:
            return
        if len(self.attachments) == 1:
            attachment = self.attachments[0]
            if attachment.type == "photo":
                await msg.answer_photo(attachment.get_input_file())
            elif attachment.type == "animation":
                await msg.answer_animation(attachment.get_input_file())
            else:
                await msg.answer_document(attachment.get_input_file())
            return
        photos: list[Attachment] = list(filter(
            lambda item: item.type == "photo", self.attachments))
        animations: list[Attachment] = list(filter(
            lambda item: item.type == "animation", self.attachments))
        documents: list[Attachment] = list(filter(
            lambda item: item.type == "document", self.attachments))

        # group photos
        if len(photos) == 1:
            await msg.answer_photo(photos[0].get_input_file())
        else:
            if len(photos) != 0:
                length: int = len(photos)
                if length > 1:
                    chunk_size = 10
                    for start in range(0, length, chunk_size):
                        if length > 10:
                            await msg.answer_media_group([InputMediaPhoto(item.get_input_file()) for item in photos[start:start + 10]])
                        else:
                            if len(photos[start:length]) > 1:
                                await msg.answer_media_group([InputMediaPhoto(item.get_input_file())for item in photos[start:length]])
                            else:
                                await msg.answer_photo(photos[length - 1].get_input_file())
                else:
                    await msg.answer_photo(photos[0].get_input_file())
            if len(documents) != 0:
                for item in documents:
                    await msg.answer_document(item.get_input_file())
            if len(animations) != 0:
                for item in animations:
                    await msg.answer_animation(item.get_input_file())

    # convert task list to unparsed type

    def convert_tasks(self) -> str:
        res = ""
        for item in self.tasks:
            res += f"\n{item.print_source()}"
        return res

    def parse_message(
        self,
        message: str
    ) -> bool:
        """
        Return False if message is not valid, True if message parsed
        """
        task_input = message.split("\n")
        # validate message
        for task_str in task_input:
            if not validate_message(task_str, ["s.", "#"]):
                return False
        # parse strings
        self.tasks = []
        for string in task_input:
            temp = Task()
            temp.parse_string(string)
            self.tasks.append(temp)
            temp = None

        return True

    def is_empty(
        self
    ) -> bool:
        if self.teacher != "" and len(self.tasks) != 0:
            return True
        return False
