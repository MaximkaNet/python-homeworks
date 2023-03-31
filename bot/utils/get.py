import requests
import pathlib
import uuid


async def get_file_path(bot_token: str, file_id: str) -> str:
    file = requests.get(
        f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}").json()
    return file["result"]["file_path"]


async def get_file(bot_token: str, file_path: str) -> bytes:
    file_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"

    res: requests.Response = requests.get(file_url, stream=True)

    return res.content
