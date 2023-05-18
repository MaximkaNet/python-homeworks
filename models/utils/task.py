from ..import Task

import json


def to_task(tuples: list[tuple]) -> list[Task] | None:
    if len(tuples) == 0:
        return None
    tasks: list[Task] = []
    for item in tuples:
        source = item[0]
        exercises = json.loads(item[1])
        sentences = json.loads(item[2])
        tasks.append(Task(source, exercises, sentences))
    return tasks
