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


def log(message: str, user: str):
    now = datetime.datetime.now()
    log_text = f"[{now.strftime(LOG_DATETIME_FORMAT)}] '{user}': {message}"
    print(log_text)
