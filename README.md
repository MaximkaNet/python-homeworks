# Telegram bot for managment homeworks.

## How to install?
Download branch or by means of git controll versions install on server with MySQL database.
Next step. Configurate bot in _config.py_, set TOKEN and database configuration.
Run **python main.py**. Enjoy ;)

## Version 1
Added commands for work with bot. All commands/actions work on states and store data in them.

## Allowed commands
  ### In private chat
  - /start, /help - show commands information
  - /addh - help with adding homeworks
  - /homework - open homework workspace (commands for work with homework)
    * /help - allowed commands for workspace
    * /show - print a homework by date (tomorrow or another date)
    * /add - add a new homework
    * /showlast(count_homeworks) - print last homeworks. count_homeworks: default 2
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