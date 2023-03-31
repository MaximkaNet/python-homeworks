from bot.database.engine.connect import connection
from mysql.connector import Error, MySQLConnection
TEACHERS_TABLE = """
CREATE TABLE IF NOT EXISTS `teachers` (
  `id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(50) NOT NULL UNIQUE
) ENGINE=InnoDB
"""
TEACHERS_WORK_DAYS = """
CREATE TABLE IF NOT EXISTS `teachers_work_days` (
  `teacher_id` int NOT NULL,
  `day` bit(7) NOT NULL,
  CONSTRAINT `teachers_work_days` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
"""
HOMEWORKS_TABLE = """
CREATE TABLE IF NOT EXISTS `homeworks` (
  `id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `date` date NOT NULL,
  `update` date NOT NULL,
  `author_id` int NOT NULL,
  CONSTRAINT `homeworks_author_id` FOREIGN KEY (`author_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
"""
HOMEWORKS_ATTACHMENTS = """
CREATE TABLE IF NOT EXISTS `attachments` (
  `id` varchar(40) NOT NULL UNIQUE,
  `name` varchar(70) NOT NULL,
  `file` mediumblob NOT NULL,
  `file_type` varchar(40) NOT NULL,
  `homework_id` int NOT NULL,
  CONSTRAINT `homeworks_files` FOREIGN KEY (`homework_id`) REFERENCES `homeworks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
"""
TASKS_TABLE = """
CREATE TABLE IF NOT EXISTS `tasks` (
  `source` text NOT NULL,
  `exercises` text NOT NULL,
  `sentences` text NOT NULL,
  `homework_id` int NOT NULL,
  CONSTRAINT `tasks_homework_id` FOREIGN KEY (`homework_id`) REFERENCES `homeworks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
"""


def check_tables(con: MySQLConnection = None) -> bool:
    try:
        if con == None:
            con = connection()
        cur = con.cursor()
        cur.execute(TEACHERS_TABLE)
        cur.execute(TEACHERS_WORK_DAYS)
        cur.execute(HOMEWORKS_TABLE)
        cur.execute(HOMEWORKS_ATTACHMENTS)
        cur.execute(TASKS_TABLE)
        con.commit()
    except Error as err:
        raise err
    else:
        return True
