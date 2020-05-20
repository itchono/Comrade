# Set of commands for music control
# Anthony Luo, May 2020.
# currently in dev.

from src.utils.music import *

class Music(commands.Cog):
    '''
    musicTM
    written by Anni.
    '''
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.check(isnotThreat)
    async def queue(selfself, ctx: commands.Context):
        '''
        queues music.
        '''