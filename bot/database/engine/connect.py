import mysql.connector as connector

from bot.utils.env import Config

from .exception import ConnectionError


def connection() -> connector.MySQLConnection:
    try:
        con = connector.connect(
            username=Config.USER,
            password=Config.PASSWORD,
            host=Config.HOST,
            database=Config.DATABASE
        )
    except connector.Error as err:
        raise ConnectionError(err)
    else:
        return con
