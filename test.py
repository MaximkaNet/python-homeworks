import db
import datetime


def test_queries():
    for i in range(0, 40):
        date = datetime.date.today() + datetime.timedelta(days=1 + i)
        id_hw = db.insert_homework(date, date, 1)
        for i in range(0, 3):
            db.insert_task(
                f"book {i}", '["test1","test2","test3","test4","test5"]', '["test sentences 1","test sentences 2","test sentences 3","test sentences 4","test sentences 5"]', id_hw)
