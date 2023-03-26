import datetime
import os

LOG_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def convert_week(days: list[int]) -> list[str]:
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    week = []
    for i, item in enumerate(days):
        week.append(day_names[item])
    return week


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


def log(func, message: str, user: str):
    log_file = "log.txt"
    log_text = f"Log: [{datetime.datetime.now().strftime(LOG_DATETIME_FORMAT)}] {func.__name__} '{user}': {message}"
    if not os.path.exists(log_file):
        with open(log_file, "w") as f:
            f.write("==== LOG FILE ====")
            f.write(f"\n{log_text}")
        print(log_text)
        return
    with open(log_file, "a") as f:
        f.write(f"\n{log_text}")
    print(log_text)
