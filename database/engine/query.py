from .connect import connection
from .exception import ConnectionError, SelectError, InsertError, UpdateError, DeleteError, AggregateError
import mysql.connector as connector

from .checker import create_tables


def select(sql: str, val: tuple = None) -> list:
    try:
        con = connection()
        # check integrity tables
        create_tables(connection=con)
        # ----
        cursor = con.cursor()
        cursor.execute(sql, val)
        records = cursor.fetchall()
    except connector.Error as err:
        raise SelectError(err)
    except ConnectionError as connErr:
        raise connErr
    else:
        if con.is_connected():
            cursor.close()
            con.close()
        return records


def insert(sql: str, val: tuple | list[tuple] = None) -> int:
    try:
        con = connection()
        # check integrity tables
        create_tables(connection=con)
        # ----
        cursor = con.cursor()
        if isinstance(val, tuple):
            cursor.execute(sql, val)
        elif isinstance(val, list):
            cursor.executemany(sql, val)
        else:
            cursor.execute(sql, val)
        con.commit()
    except connector.Error as err:
        raise InsertError(err)
    except ConnectionError as connErr:
        raise connErr
    else:
        if con.is_connected():
            cursor.close()
            con.close()
        return cursor.lastrowid


def update(sql: str, val: tuple = None) -> None:
    try:
        con = connection()
        # check integrity tables
        create_tables(connection=con)
        # ----
        cursor = con.cursor()
        cursor.execute(sql, val)
        con.commit()
    except connector.Error as err:
        raise UpdateError(err)
    except ConnectionError as connErr:
        raise connErr
    else:
        if con.is_connected():
            cursor.close()
            con.close()


def delete(sql: str, val: tuple = None) -> None:
    try:
        con = connection()
        # check integrity tables
        create_tables(connection=con)
        # ----
        cursor = con.cursor()
        cursor.execute(sql, val)
        con.commit()
    except connector.Error as err:
        raise DeleteError(err)
    except ConnectionError as connErr:
        raise connErr
    else:
        if con.is_connected():
            cursor.close()
            con.close()


def aggregate(sql, val: tuple = None) -> list:
    try:
        con = connection()
        # check integrity tables
        create_tables(connection=con)
        # ----
        cursor = con.cursor()
        cursor.execute(sql, val)
        res = cursor.fetchall()
    except connector.Error as err:
        raise AggregateError(err)
    except ConnectionError as connErr:
        raise connErr
    else:
        if con.is_connected():
            cursor.close()
            con.close()
        return res
