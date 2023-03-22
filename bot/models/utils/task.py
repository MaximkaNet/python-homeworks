from bot import models

import json


def convert_to_list(tuples: list[tuple]) -> list[models.Task]:
    if len(tuples) == 0:
        return []
    tasks: list[models.Task] = []
    for item in tuples:
        tasks.append(models.Task(item[0], json.loads(
            item[1]), json.loads(item[2])))
    return tasks
