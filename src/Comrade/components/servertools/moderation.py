import discord
from discord.ext import commands


class Moderation(commands.Cog):
    pass

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        '''
        Prepare moderation filters
        '''
        # If user is a threat, raise shields