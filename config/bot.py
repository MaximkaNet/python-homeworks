from os import environ
from typing import Final
from dotenv import load_dotenv

load_dotenv()


class FrontBotConfig:
    TOKEN: Final = environ.get("FRONTEND_TOKEN", "")
    PROXY: Final = environ.get("PROXY", "http://proxy.server:3128")


class AdminBotConfig:
    TOKEN: Final = environ.get("ADMIN_TOKEN", "")
    PROXY: Final = environ.get("PROXY", "http://proxy.server:3128")
