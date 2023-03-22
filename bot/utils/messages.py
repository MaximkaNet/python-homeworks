WELLCOME_USER = """
This is homework managment bot.

Select mode:
/homework - homework managment panel
/teacher - teacher managment panel
"""
WELLCOME_GROUP = """
This is homework managment bot.

/homework - Show last homework
"""
HELP_ADD = """
To add a new task:
1. Select a teacher.
2. Write homework in the correct format:

_Pracak: s.13() # some text 2... s.123(1,23)_
or
_Some book1: s.1() s.12 #some text... s.12(1,2a)_
_Some book2: s.12() s.1 #some text..._

*Tasks must be written in one line without hyphenation!*
"""
SELECT_TEACHER = "Select a teacher:"
TCH_PANEL_COMMANDS = """Commands:
/add - add a new teacher
/show - all teachers
/changename - change a teacher name
/close - exit from managment panel"""
HW_PANEL_COMMANDS = """Commands:
/add - add a new homework
/show - show a homework
/showlast - show homeworks. You can write the command /showlast<count>
/close - exit from managment panel"""
ADD_TASK = """
Write your homework in this format:
_<source>: s.<page> (numbers) # something..._

You can learn more about adding a task with the command /addh
You can /cancel this action
"""
TEACHER_PANEL_WELLCOME = "Wellcome to *teacher* managment panel."
HOMEWORK_PANEL_WELLCOME = "Wellcome to *homework* managment panel."
HOMEWORK_PANEL_BYE = "*Homework* managment panel was closed. /help"
TEACHER_PANEL_BYE = "*Teacher* managment panel was closed. /help"
HOMEWORK_ADDED = "Complete. /help"
HOMEWORK_EDITED = "Complete. /help"
TEACHER_ADDED = "Complete. /help"
TEACHER_EDITED = "Complete. /help"
HOMEWORKS_NOT_FOUND = "Homeworks is not found. /help"
TEACHERS_NOT_FOUND = "Teachers is not found. /help"
HOMEWORK_UPDATE_QUESTION = "Homework already exist.\nYou want edit it?\n*Yes / No*"
EDIT_INSTRUCTION = "1.Copy next text.\n2.Paste.\n3.Edit and send."
ACTION_CANCELED = "Action was canceled. /help"
INCORRECT = "Incorrect answer!"
HOMEWORK_DELETED = "Deleted."
