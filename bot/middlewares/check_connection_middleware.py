import logging

from database.engine.connect import connection
from database.engine.exception import ConnectionError
from ..utils.messages import SERVICE_UNAVAILABLE


async def check_connection() -> tuple[str, bool]:
    """
    The fisrt param: message
    The second param: access flag
    """
    try:
        connection()
    except ConnectionError:
        logging.critical("Database connection unavailable.")
        return (SERVICE_UNAVAILABLE, False)
    else:
        return ("Service available.", True)
