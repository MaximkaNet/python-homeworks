from aiogram.types import InputFile
from io import BytesIO

from database.methods import select


def get_files(homework_id: int) -> list:
    selected_files = select.homework_files(homework_id)
    files = []
    photos = []
    animations = []
    for row in selected_files:
        name = row[1]
        file = row[2]
        file_type = row[3]
        if file_type == "photo":
            photos.append(InputFile(BytesIO(file), name))
        elif file_type == "animation":
            animations.append(InputFile(BytesIO(file), name))
        else:
            files.append(InputFile(BytesIO(file), name))
    return (photos, files, animations)
