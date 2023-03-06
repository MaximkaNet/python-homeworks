from os import environ
from typing import Final


class Config:
    TOKEN: Final = environ.get(
        "TOKEN", "YOUR TOKEN")
    HOST: Final = environ.get("HOST", "HOST")
    USER: Final = environ.get("USER", "DB USER")
    PASSWORD: Final = environ.get("PASSWORD", "DB PASSWORD")
    DATABASE: Final = environ.get("DATABASE", "DB NAME")
    PROXY: Final = environ.get(
        "PROXY", "http://proxy.server:3128")  # telegram proxy
