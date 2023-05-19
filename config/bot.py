from os import environ
from typing import Final
from dotenv import load_dotenv

load_dotenv()


class BotConfig:
    TOKEN: Final = environ.get("TOKEN", "")
    PROXY: Final = environ.get("PROXY", "http://proxy.server:3128")
