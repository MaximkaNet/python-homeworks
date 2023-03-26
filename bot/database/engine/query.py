from .connect import connection
from .exception import ConnectionError, SelectError, InsertError, UpdateError, DeleteError, AggregateError
import mysql.connector as connector


def select(sql: str, val: tuple = None):
    try:
        con = connection()
        cursor = con.cursor()
        cursor.execute(sql, val)
        records = cursor.fetchall()
    except connector.Error as err:
        raise SelectError(err)
    except ConnectionError as connErr:
        raise connErr
    else:
        return records


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
        raise InsertError(err)
    except ConnectionError as connErr:
        raise connErr
    else:
        return cursor.lastrowid


def update(sql: str, val: tuple = None):
    try:
        con = connection()
        cursor = con.cursor()
        cursor.execute(sql, val)
        con.commit()
    except connector.Error as err:
        raise UpdateError(err)
    except ConnectionError as connErr:
        raise connErr


def delete(sql: str, val: tuple = None):
    try:
        con = connection()
        cursor = con.cursor()
        cursor.execute(sql, val)
        con.commit()
    except connector.Error as err:
        raise DeleteError(err)
    except ConnectionError as connErr:
        raise connErr


def aggregate(sql, val: tuple = None):
    try:
        con = connection()
        cursor = con.cursor()
        cursor.execute(sql, val)
    except connector.Error as err:
        raise AggregateError(err)
    except ConnectionError as connErr:
        raise connErr
    else:
        return cursor.fetchall()
