WELLCOME_USER = """
This is homework managment bot.

/add - Add new homework
/homework - Show last homework
/all - Show all homeworks

/hadd - About add function
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

# Add functions
ADD_TASK = """
Write your homework in this format:
_<source>: s.<page>(numbers) #something..._

You can learn more about adding a task with the command /hadd
You can /cancel this action
"""
ADDING_HOMEWORK_COMPLETED = "Complete. \nYou can see /homework"

HOMEWORKS_NOT_FOUND = "Homeworks is not found."
EDIT_INSTRUCTION = "1.Copy next text.\n2.Paste.\n3.Edit and send."
ACTION_CANCELED = "Action was canceled."
