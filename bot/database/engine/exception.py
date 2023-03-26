class DBException(Exception):
    def __init__(self, type: str, msg: str) -> None:
        self.type = type
        self.msg = msg

    def __str__(self) -> str:
        return f"{self.type}: {self.msg}"

# connection error


class ConnectionError(DBException):
    def __init__(self, message: str) -> None:
        super().__init__("ConnectionError", message)

# query errors


class QueryError(DBException):
    def __init__(self, method: str, message: str) -> None:
        super().__init__(f"{method}QueryError", message)


class SelectError(QueryError):
    def __init__(self, message: str) -> None:
        super().__init__("Select", message)


class InsertError(QueryError):
    def __init__(self, message: str) -> None:
        super().__init__("Insert", message)


class UpdateError(QueryError):
    def __init__(self, message: str) -> None:
        super().__init__("Update", message)


class DeleteError(QueryError):
    def __init__(self, message: str) -> None:
        super().__init__("Delete", message)


class AggregateError(QueryError):
    def __init__(self, message: str) -> None:
        super().__init__("Aggregate", message)
