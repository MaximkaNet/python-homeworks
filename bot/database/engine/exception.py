class DBException(Exception):
    def __init__(self, type: str, msg: str) -> None:
        self.type = type
        self.msg = msg

    def __str__(self) -> str:
        return self.msg
