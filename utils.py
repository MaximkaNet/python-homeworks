import datetime

LOG_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def trim(str: str) -> str:
    word_list = str.split(" ")
    res = ""
    size = len(word_list)
    for i, word in enumerate(word_list):
        if word != "":
            res += word
            if i < size - 1:
                res += " "
    res = res.strip()
    return res


def debug(func, *message: str):
    print(f"Debug: [{datetime.datetime.now().strftime(LOG_DATETIME_FORMAT)}] {func.__module__}.{func.__name__}: ", *message)


def log(func, *message: str, user: str):
    print(f"Log: [{datetime.datetime.now().strftime(LOG_DATETIME_FORMAT)}] {func.__module__}.{func.__name__} '{user}':", *message)
