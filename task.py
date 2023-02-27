import json
import utils


class Task:
    def __init__(self, source: str = "", exercises: list = [], sentences: list = []):
        self.source: str = source
        self.exercises: list[str] = exercises
        self.sentences: list[str] = sentences

    def print(self, separator: str = "|-") -> str:
        ex_str = ""
        for ex in self.exercises:
            ex_str += f"\n{separator} s.{ex}"
        sen_str = ""
        for sen in self.sentences:
            sen_str += f"\n{separator} {sen}"
        return f"\n{self.source}:{ex_str}{sen_str}"

    # converter

    def convert_unparsed(self) -> str:
        res = ""
        for item in self.exercises:
            res += f"s.{item} "
        for item in self.sentences:
            res += f"#{item} "
        return f"{self.source}: {res}"
    # string parser

    def string_parser(self, str: str):
        str = utils.trim(str)
        end_source_index = str.find(":")
        self.source = str[0:end_source_index]
        self.exercises = []
        self.sentences = []
        start_index = end_source_index
        str_length = len(str)
        while True:
            case1 = str.find("s.", start_index)
            case2 = str.find("#", start_index)
            if case1 == -1 and case2 == -1:
                break
            if case1 != -1 and case2 != -1:
                if case1 < case2:  # find exercises
                    end_case1 = str.find("s.", case1 + 2)
                    end_case2 = str.find("#", case1 + 2)
                    # end of string
                    if end_case1 == -1 and end_case2 == -1:
                        self.exercises.append(str[case1 + 2:str_length])
                        break

                    if end_case1 != -1 and end_case2 != -1:
                        if end_case1 < end_case2:
                            self.exercises.append(
                                str[case1 + 2: end_case1 - 1])
                            start_index = end_case1 - 1
                        else:
                            self.exercises.append(
                                str[case1 + 2: end_case2 - 1])
                            start_index = end_case2 - 1
                    elif end_case1 != -1:
                        self.exercises.append(
                            str[case1 + 2: end_case1 - 1])
                        start_index = end_case1 - 1
                    elif end_case2 != -1:
                        self.exercises.append(
                            str[case1 + 2: end_case2 - 1])
                        start_index = end_case2 - 1
                else:  # find sentences
                    end_case1 = str.find("s.", case2 + 1)
                    end_case2 = str.find("#", case2 + 1)
                    if end_case1 == -1 and end_case2 == -1:
                        self.sentences.append(str[case2 + 1: str_length])
                        break

                    if end_case1 != -1 and end_case2 != -1:
                        if end_case1 < end_case2:
                            self.sentences.append(
                                str[case2 + 1: end_case1 - 1])
                            start_index = end_case1 - 1
                        else:
                            self.sentences.append(
                                str[case2 + 1: end_case2 - 1])
                            start_index = end_case2 - 1
                    elif end_case1 != -1:
                        self.sentences.append(
                            str[case2 + 1: end_case1 - 1])
                        start_index = end_case1 - 1
                    elif end_case2 != -1:
                        self.sentences.append(
                            str[case2 + 1: end_case2 - 1])
                        start_index = end_case2 - 1
            elif case1 != -1:  # exercises
                end_case1 = str.find("s.", case1 + 2)
                end_case2 = str.find("#", case1 + 2)
                if end_case1 == -1 and end_case2 == -1:
                    self.exercises.append(str[case1 + 2: str_length])
                    break

                if end_case1 != -1 and end_case2 != -1:
                    if end_case1 < end_case2:
                        self.exercises.append(
                            str[case1 + 2: end_case1 - 1])
                        start_index = end_case1 - 1
                    else:
                        self.exercises.append(
                            str[case1 + 2: end_case2 - 1])
                        start_index = end_case2 - 1
                elif end_case1 != -1:
                    self.exercises.append(
                        str[case1 + 2: end_case1 - 1])
                    start_index = end_case1 - 1
                elif end_case2 != -1:
                    self.exercises.append(
                        str[case1 + 2: end_case2 - 1])
                    start_index = end_case2 - 1
            elif case2 != -1:  # sentences
                end_case1 = str.find("s.", case2 + 1)
                end_case2 = str.find("#", case2 + 1)
                if end_case1 == -1 and end_case2 == -1:
                    self.sentences.append(str[case2 + 1: str_length])
                    break

                if end_case1 != -1 and end_case2 != -1:
                    if end_case1 < end_case2:
                        self.sentences.append(
                            str[case2 + 1: end_case1 - 1])
                        start_index = end_case1 - 1
                    else:
                        self.sentences.append(
                            str[case2 + 1: end_case2 - 1])
                        start_index = end_case2 - 1
                elif end_case1 != -1:
                    self.sentences.append(
                        str[case2 + 1: end_case1 - 1])
                    start_index = end_case1 - 1
                elif end_case2 != -1:
                    self.sentences.append(
                        str[case2 + 1: end_case2 - 1])
                    start_index = end_case2 - 1
        return self
    # validator

    def validate_message(str: str) -> bool:
        start = str.find(":", 0)
        return False if start == -1 else True if str.find("s.", start) != -1 or str.find("#", start) != -1 else False


def convert_to_list(tuples: list[tuple]) -> list[Task]:
    if len(tuples) == 0:
        return []
    tasks: list[Task] = []
    for item in tuples:
        tasks.append(Task(item[0], json.loads(item[1]), json.loads(item[2])))
    return tasks
