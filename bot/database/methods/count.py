from bot.database.engine.query import aggregate

from bot.database.engine.exception import ConnectionError, DBException
import logging


def teachers():
    sql = "SELECT COUNT(*) FROM `teachers`"
    try:
        res = aggregate(sql)[0][0]
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)
    else:
        return res


def homeworks():
    sql = "SELECT COUNT(*) FROM `homeworks`"
    try:
        res = aggregate(sql)[0][0]
    except ConnectionError as err:
        logging.critical(err)
    except DBException as err:
        logging.error(err)
    else:
        return res
