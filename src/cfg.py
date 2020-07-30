# version of the bot
VERSION = "3.2 [Build July 30 v1]" 

# set to True if you are testing the bot in a development environment, False otherwise
DEVELOPMENT_MODE = False 

# change depending on host location.
LOCAL_TIMEZONE = 'Canada/Eastern' 

# the thing you type at the beginning of a command
BOT_PREFIX = "$c " 

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

