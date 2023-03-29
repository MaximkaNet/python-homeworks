from bot.utils import trim


class Task:
    def __init__(self, source: str = "", exercises: list = [], sentences: list = []) -> None:
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
        str = trim(str)
        # find source
        end_source_index = str.find(":")
        self.source = str[0:end_source_index]

        self.exercises = []
        self.sentences = []

        separators = ["s.", "#"]
        data_vars = {
            "s.": self.exercises,
            "#": self.sentences
        }
        # find records
        start_index = end_source_index
        str_length = len(str)
        start_pos, sp = Task.find_closest_separator(
            separators, str, start_index)
        while start_index != str_length:
            # closest start separator
            end_pos, end_sp = Task.find_closest_separator(
                separators, str, start_pos + len(sp))
            if end_pos == -1:
                data_vars[sp].append(
                    str[start_pos + len(sp):str_length].strip())
                break
            # separators
            data_vars[sp].append(str[start_pos + len(sp):end_pos].strip())
            start_pos = end_pos
            sp = end_sp
            start_index = end_pos
        return self

    def find_closest_separator(_separators: list[str], _str: str, _start_index: int = 0) -> tuple[int, str]:
        sp = ""
        min_pos = len(_str)
        for item in _separators:
            sp_pos = _str.find(item, _start_index)
            if 0 < sp_pos < min_pos:
                min_pos = sp_pos
                sp = item
        return (min_pos, sp) if sp != "" else (-1, None)
    # validator

    def validate_message(str: str) -> bool:
        start = str.find(":", 0)
        return False if start == -1 else True if str.find("s.", start) != -1 or str.find("#", start) != -1 else False
