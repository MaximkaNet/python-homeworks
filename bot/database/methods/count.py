from bot.database.engine.query import aggregate


def teachers():
    sql = "SELECT COUNT(*) FROM `teachers`"
    return aggregate(sql)[0][0]


def homeworks():
    sql = "SELECT COUNT(*) FROM `homeworks`"
    return aggregate(sql)[0][0]
