from ..engine.query import query


class count:
    def teachers():
        sql = "SELECT COUNT(*) FROM `teachers`"
        return query.aggregate(sql)[0][0]

    def homeworks():
        sql = "SELECT COUNT(*) FROM `homeworks`"
        return query.aggregate(sql)[0][0]
