# Telegram bot for managment homeworks.

## How to install?
Install requirements ```pip install -r requirements.txt```.
Download branch or by means of git controll versions install on server with MySQL database.
### Next step.
Create `.env` file and add a few rows
```
TOKEN=YOUR TOKEN
HOST=YOUR HOST
USER=DATABASE USER
PASSWORD=DATABASE PASSWAORD
DATABASE=DATABASE NAME
PROXY=None
``` 
`PROXY` will be `None` if you start bot in local machine. You can leave this field blank.
Run ```python run.py```. Enjoy ;)

## Version 1.2.1
Add new command `/today`


## Allowed commands
  ### In private chat
  *--- Show ---*
  #### _Homework_:
  - `/tomorrow` - show tomorrow homework
  - `/anotherdate` - show homework for other date using callendar
  - `/today` - show today homework
  #### _More items_:
  - `/hws` - print list homeworks
  - `/teachers` - show list teachers

  *--- Add ---*
  #### _Teacher_:
  - `/newteacher` - add new teacher

  #### _Homework_:
  - `/newhw` - add new

  `/about` - about project
  ### In group/supergroup chat
  - `/tomorrow` - show tomorrow homework
  - `/anotherdate` - show homework for other date using callendar
  - `/about` - about project