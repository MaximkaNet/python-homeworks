import mysql.connector as connector

from ..config import tables


def create_tables(connection: connector.MySQLConnection = None) -> None:
    if connection == None:
        connection = connection()
    cursor = connection.cursor()
    cursor.execute(tables.TEACHERS_TABLE)
    cursor.execute(tables.TEACHERS_WORK_DAYS)
    cursor.execute(tables.HOMEWORKS_TABLE)
    cursor.execute(tables.HOMEWORKS_ATTACHMENTS)
    cursor.execute(tables.TASKS_TABLE)
    connection.commit()
