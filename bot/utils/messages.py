WELLCOME = """
Wellcome to homework managment system.

You can see my commands using /help
"""

HELP = f"""
Available commands:

/tomorrow - show tomorrow homework
/anotherdate - show homework for other date using callendar

/about - about project
"""

HELP_ADMIN = f"""
Available commands for homework:

*--- Show ---*
_Homework_:
/tomorrow - show tomorrow homework
/anotherdate - show homework for other date using callendar

/hws - print list homeworks
/teachers - show list teachers

*--- Add ---*
_Teacher_:
/newteacher - add new teacher

_Homework_:
/newhw - add new

/about - about project
"""

HELP_DEV = f"""
_/lastbyteacher - show homework for teacher's next work day_

_/setname - change name_
_/setworkdays - change work days_

_/newhwdate - add new for selected date_
"""

ABOUT = """
Thank you for using.
All source code you can see on the [github](https://github.com/MaximkaNet/python-homeworks)
"""

SERVICE_UNAVAILABLE = "The service is not available. Please try again later. /help"

HOMEWORKS_NOT_FOUND = "Homeworks is not found. /help"
TEACHERS_NOT_FOUND = "Teachers is not found. /help"

ADD_TEACHER = "Ok. Type a name."
ADD_WORK_DAYS = "Add a work days."
WORK_DAYS_IS_EMPTY = "Please, try once."
COMPLETE_ADD_TEACHER = "Complete! /help"

ADD_DATA_HOMEWORK = """
Send homework in the correct format:

_source   task1   task2_
   👇      👇     👇
_Pracak: s.13() # some text 2... s.123(1,23)_
or
_Some book1: s.1() s.12 #some text... s.12(1,2a)_
_Some book2: s.12() s.1 #some text..._

*Tasks must be written in one line without hyphenation!*
/help
"""

SELECT_TEACHER = "Who you want to assign this homework to?\nPlease, select."

HOMEWORK_HAS_BEEN_ADDED = "Homework has been added success.\nYou can send me files/photos\nor add /newhw\nCommands - /help"

HOMEWORK_ALREADY_EXIST = "Homework already exist./help"
HOMEWORK_INCORRECT_FORMAT = "Incorrect homework format!/help"
FILE_HAS_BEEN_ADDED = "File has been added."
