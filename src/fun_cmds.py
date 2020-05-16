from utils.utilities import *
from utils.mongo_interface import *


class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        pass
