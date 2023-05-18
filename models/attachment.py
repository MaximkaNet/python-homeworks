from database.methods import insert
from aiogram.types import InputFile
from io import BytesIO


class Attachment:
    def __init__(
        self,
        id: str | None,
        name: str,
        blob: bytes,
        type: str
    ) -> None:
        self.id = id
        self.name = name
        self.blob = blob
        self.type = type

    def insert(
        self,
        homework_id: int
    ) -> None:
        insert.homework_file(name=self.name,
                             blob=self.blob,
                             type=self.type,
                             homework_id=homework_id)

    def get_input_file(
        self
    ) -> InputFile:
        return InputFile(BytesIO(self.blob), self.name)
