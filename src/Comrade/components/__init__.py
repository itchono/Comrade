from typing import Text
from .general import General, Macros, Go, Music, Slash
from .fun import Fun, RandomEvents, Echo
from .tools import Tools, Textgen, Lists, Reminders
from .games import Games
from .servertools import (Databases, Emotes, Users,
                          Announcements, Vault, Moderation,
                          TextFilter, Copier, Sniper)
from .nsfw import NSFW

# The cogs to be loaded by the bot at runtime
cogs = [General, Fun, Tools, Textgen, Games,
        Emotes, Users, Echo, Macros,
        Reminders, Lists, RandomEvents,
        Databases, Announcements, Sniper,
        Vault, Moderation, TextFilter,
        Copier, NSFW, Go, Music]
