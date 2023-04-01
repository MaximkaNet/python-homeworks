# Telegram bot for managment homeworks.

## How to install?
Download branch or by means of git controll versions install on server with MySQL database.
Next step. Configurate bot in _bot/utils/env.py_, set TOKEN and database configuration.
Run **python run.py**. Enjoy ;)

## Version 1.1
Restructuring bot.
Added attachments to homeworks support.
New command /addempty for adding empty homework if no homework has been given.


## Allowed commands
  ### In private chat
  - /start, /help - show commands information
  - /addh - help with adding homeworks
  - /homework - open homework workspace (commands for work with homework)
    * /help - allowed commands for workspace
    * /show - print a homework by date (tomorrow or another date)
    * /add - add a new homework
    * /showlast(count_homeworks) - print last homeworks. count_homeworks: default 2
    * /addempty - add empty homework
    * /close - close workspace
  - /teacher - open teacher workspace (commands for work with teacher)
    * /help - show allowed commands for workspace
    * /add - add a new teacher
    * /show - show *all* teachers
    * /changename - change name for selected teacher
    * /close - close workspace
  ### In group/supergroup chat
  - /start, /help - show commands information
  - /homework - print a homework by date (tomorrow ar another date) 