TEACHERS_TABLE = """
CREATE TABLE IF NOT EXISTS `teachers` (
  `id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `surname` varchar(50) NULL,
  `position` varchar(50) NULL
) ENGINE=InnoDB
"""
TEACHERS_WORK_DAYS = """
CREATE TABLE IF NOT EXISTS `teachers_work_days` (
  `teacher_id` int NOT NULL,
  `day` bit(7) NOT NULL,
  `day_name` varchar(10) NULL,
  CONSTRAINT `teachers_work_days` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
"""
HOMEWORKS_TABLE = """
CREATE TABLE IF NOT EXISTS `homeworks` (
  `id` int NOT NULL PRIMARY KEY AUTO_INCREMENT,
  `created_at` date NOT NULL,
  `updated_at` date NOT NULL,
  `teacher_id` int NOT NULL,
  CONSTRAINT `homeworks_teacher_id` FOREIGN KEY (`teacher_id`) REFERENCES `teachers` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB
"""
HOMEWORKS_ATTACHMENTS = """
CREATE TABLE IF NOT EXISTS `attachments` (
  `id` varchar(40) NOT NULL UNIQUE,
  `file_name` varchar(70) NOT NULL,
  `file_type` varchar(40) NOT NULL,
  `file_blob` mediumblob NOT NULL,
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
