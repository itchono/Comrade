from Utilities import *


class AuxilliaryListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:discord.Reaction, user:discord.User):
    
        # self-cleanup
        if reaction.message.author == self.bot.user and reaction.emoji == "🗑️" and user != self.bot.user:
            await reaction.message.delete()
