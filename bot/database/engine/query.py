from .connect import connection
from .exception import DBException
import mysql.connector as connector


class query:
    def select(sql: str, val: tuple = None):
        try:
            con = connection()
            cursor = con.cursor()
            cursor.execute(sql, val)
            records = cursor.fetchall()
            return records
        except connector.Error as err:
            raise DBException("Query select", err)

    def insert(sql: str, val: tuple | list[tuple] = None) -> int:
        try:
            con = connection()
            cursor = con.cursor()
            if isinstance(val, tuple):
                cursor.execute(sql, val)
            elif isinstance(val, list):
                cursor.executemany(sql, val)
            else:
                cursor.execute(sql, val)
            con.commit()
        except connector.Error as err:
            raise DBException("Query insert", err)
        finally:
            return cursor.lastrowid

    def update(sql: str, val: tuple = None):
        try:
            con = connection()
            cursor = con.cursor()
            cursor.execute(sql, val)
            con.commit()
        except connector.Error as err:
            raise DBException("Query update", err)

    def delete(sql: str, val: tuple = None):
        try:
            con = connection()
            cursor = con.cursor()
            cursor.execute(sql, val)
            con.commit()
        except connector.Error as err:
            raise DBException("Query delete", err)

    def aggregate(sql, val: tuple = None):
        try:
            con = connection()
            cursor = con.cursor()
            cursor.execute(sql, val)
        except connector.Error as err:
            raise DBException("Query aggregate", err)
        finally:
            return cursor.fetchall()
