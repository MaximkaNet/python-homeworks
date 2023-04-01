from .connect import connection
from .exception import ConnectionError, SelectError, InsertError, UpdateError, DeleteError, AggregateError
import mysql.connector as connector
from bot.middlewares import check_tables


def select(sql: str, val: tuple = None) -> list:
    try:
        con = connection()
        check_tables(con)
        cursor = con.cursor()
        cursor.execute(sql, val)
        records = cursor.fetchall()
    except connector.Error as err:
        raise SelectError(err)
    except ConnectionError as connErr:
        raise connErr
    else:
        return records
    finally:
        if con.is_connected():
            cursor.close()
            con.close()


def insert(sql: str, val: tuple | list[tuple] = None) -> int:
    try:
        con = connection()
        check_tables(con)
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
    finally:
        if con.is_connected():
            cursor.close()
            con.close()


def update(sql: str, val: tuple = None) -> None:
    try:
        con = connection()
        check_tables(con)
        cursor = con.cursor()
        cursor.execute(sql, val)
        con.commit()
    except connector.Error as err:
        raise UpdateError(err)
    except ConnectionError as connErr:
        raise connErr
    finally:
        if con.is_connected():
            cursor.close()
            con.close()


def delete(sql: str, val: tuple = None) -> None:
    try:
        con = connection()
        check_tables(con)
        cursor = con.cursor()
        cursor.execute(sql, val)
        con.commit()
    except connector.Error as err:
        raise DeleteError(err)
    except ConnectionError as connErr:
        raise connErr
    finally:
        if con.is_connected():
            cursor.close()
            con.close()


def aggregate(sql, val: tuple = None) -> list:
    try:
        con = connection()
        check_tables(con)
        cursor = con.cursor()
        cursor.execute(sql, val)
    except connector.Error as err:
        raise AggregateError(err)
    except ConnectionError as connErr:
        raise connErr
    else:
        return cursor.fetchall()
    finally:
        if con.is_connected():
            cursor.close()
            con.close()
