import mysql.connector as connector

from ..config.connection import Connection

from .exception import ConnectionError


def connection() -> connector.MySQLConnection:
    try:
        con = connector.connect(
            username=Connection.USER,
            password=Connection.PASSWORD,
            host=Connection.HOST,
            database=Connection.DATABASE
        )
    except connector.Error as err:
        raise ConnectionError(err)
    else:
        return con
