import mysql.connector as connector
from ...utils.env import Config
from .exception import DBException


def connection():
    try:
        con = connector.connect(
            username=Config.USER,
            password=Config.PASSWORD,
            host=Config.HOST,
            database=Config.DATABASE
        )
    except connector.Error as err:
        raise DBException("Connection", f"Connection error: {err}")
    finally:
        return con
