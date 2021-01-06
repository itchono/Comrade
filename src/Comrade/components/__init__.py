from .general import General, MessageTriggers
from .fun import Fun, RandomEvents, Echo
from .tools import Tools, Textgen
from .games import Games
from .servertools import Databases, Emotes, Users, Announcements

# The cogs to be loaded by the bot at runtime
cogs = [General, Textgen, Fun, RandomEvents,
        Tools, Games, Databases, Emotes,
        Users, Announcements, Echo, MessageTriggers]
