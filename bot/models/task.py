from bot.helpers.stringparser import string_parser as str_parse


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

    def parse_string(self, str: str):
        separators = ["s.", "#"]

        parsed_source, parsed_data_vars = str_parse(str, separators)

        self.source = parsed_source
        self.exercises = parsed_data_vars["#"]
        self.exercises = parsed_data_vars["s."]

        return self
