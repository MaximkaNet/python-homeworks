import logging

from bot.database.engine.connect import connection
from bot.database.engine.exception import ConnectionError


def check_connection():
    try:
        connection()
    except ConnectionError:
        logging.critical("Database connection unavailable.")
        return False
    else:
        return True
