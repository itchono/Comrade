from utils.utilities import *
from utils.mongo_interface import *

class Vault(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def randomvaultpost(self, ctx):
        '''
        Returns a random post from the vault.
        '''
        vault = getChannel(ctx.guild, "vault channel")

        msgs = vault.messages