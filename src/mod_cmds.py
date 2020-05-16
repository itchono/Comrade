from utils.utilities import *
from utils.mongo_interface import *


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
