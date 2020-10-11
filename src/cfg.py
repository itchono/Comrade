# version of the bot
VERSION = "4.0 [Build October 10]" 

# set to True if you are testing the bot in a development environment, False otherwise
DEVELOPMENT_MODE = True

# set to True if you're hosting the bot on something like repl.it or heroku and need the bot to keep alive
SELFPING_REQUIRED = False

# change depending on host location.
LOCAL_TIMEZONE = 'Canada/Eastern' 

# the thing you type at the beginning of a command
BOT_PREFIX = "$c " 
SECONDARY_PREFIX = ".c " # default: None

# default status of the bot
DEFAULT_STATUS = "[{}] Mechanizing Communism".format(BOT_PREFIX) 

# max number of active polymorph models (affects RAM)
RAM_LIMIT = 10 

# number of messages to be stored per user in buffer for moderation (affects RAM)
MSG_BUFFER_LIMIT = 10 

# maximum amount of time allowable for program execution (can affect performance)
MACRO_TIMEOUT = 15

# notifies the bot owner on startup
NOTIFY_OWNER_ON_STARTUP = True

### NAMES OF EACH DB COLLECTION ###
USER_COL = "UserData"
SERVERCFG_COL = "cfg"
CUSTOMUSER_COL = "CustomUsers"
ANNOUNCEMENTS_COL = "announcements"
CMD_COL = "CustomCommands"
LIST_COL = "CustomLists"
CACHE_COL = "ChannelCache"
FAVOURITES_COL = "favourites"
PNG_COL = "pngs"

