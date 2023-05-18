from aiogram.types import InputFile
from io import BytesIO

from models.attachment import Attachment


def convert_week(days: set[int]) -> list[str]:
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    week = []
    for item in days:
        week.append(day_names[item])
    return week


def convert_to_inputfile(files: list[Attachment] | Attachment) -> list[InputFile] | InputFile:
    if isinstance(files, list):
        return [InputFile(BytesIO(item.blob), item.name) for item in files]
    elif isinstance(files, Attachment):
        return InputFile(BytesIO(files.blob), files.name)
    else:
        raise Exception("Unknown value type")
