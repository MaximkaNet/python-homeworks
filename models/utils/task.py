from ..import Task

import json


def to_task(objs: list[tuple] | None) -> list[Task] | None:
    if objs == None:
        return None

    tasks: list[Task] = []
    for item in objs:
        source = item['source']
        exercises = json.loads(item['exercises'])
        sentences = json.loads(item['sentences'])

        tasks.append(Task(
            source=source,
            exercises=exercises,
            sentences=sentences))

    return tasks
