from .general_cmds import General
from .textgen import Textgen
from .fun import Fun, RandomEvents, Echo
from .tools import Tools
from .games import Games
from .servertools import Databases, Emotes, Users, Announcements

# The cogs to be loaded by the bot at runtime
cogs = [General, Textgen, Fun, RandomEvents,
        Tools, Games, Databases, Emotes,
        Users, Announcements, Echo]
