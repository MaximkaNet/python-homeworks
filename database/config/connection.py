import os
from typing import Final
from dotenv import load_dotenv

load_dotenv()


class Connection:
    """
    HOST - your host name like localhost
    USER - your username from database
    PASSWORD - your password from database
    DATABASE - database name
    """
    HOST: Final = os.environ.get("HOST", "")
    USER: Final = os.environ.get("USER", "")
    PASSWORD: Final = os.environ.get("PASSWORD", "")
    DATABASE: Final = os.environ.get("DATABASE", "bot")
