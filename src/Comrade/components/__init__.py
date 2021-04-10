from .general import General, Macros, Go, Slash
from .fun import Fun, RandomEvents, Echo, Youtube
from .tools import Tools, Textgen, Lists, Reminders
from .games import Games
from .servertools import (Databases, Emotes, Users,
                          Announcements, Vault, Moderation,
                          TextFilter)
from .nsfw import NSFW

# The cogs to be loaded by the bot at runtime
cogs = [General, Fun, Tools, Textgen, Games,
        Emotes, Users, Echo, Macros,
        Reminders, Lists, RandomEvents,
        Databases, Announcements, Vault,
        Moderation, TextFilter,
        NSFW, Go, Slash, Youtube]
