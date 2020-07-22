# version of the bot
VERSION = "3.1 [Build July 22 v1]" 

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

# TODO PER-SERVER
# amount of daily member counts everyone starts with
DEFAULT_DAILY_COUNT = 2 

# main colour for server; used in embeds
THEME_COLOUR = (215, 52, 42)

# colour for daily member (RGB)
DAILY_MEMBER_COLOUR = (241, 196, 15) 

# enforces recency for daily members, in days. Set to -1 (or less) to disable.
DAILY_MEMBER_STALENESS = 15 

# time to vote for ZA HANDO, in seconds
ZA_HANDO_VOTE_DURATION = 120 

# time to vote for Vault post, in seconds
VAULT_VOTE_DURATION = 180 