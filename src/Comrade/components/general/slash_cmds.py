from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash import cog_ext

guild_ids = [419214713252216848, 709954286376976425]


class Slash(commands.Cog):
    '''
    Slash commands for Discord
    '''
    def __init__(self, bot):
        if not hasattr(bot, "slash"):
            # Creates new SlashCommand instance to bot if bot doesn't have.
            bot.slash = SlashCommand(bot, override_type=True, auto_register=True, auto_delete=True)
        self.bot = bot
        self.bot.slash.get_cog_commands(self)

    @cog_ext.cog_slash(name="test", guild_ids=guild_ids)
    async def _test(self, ctx: SlashContext):
        await ctx.send(content="hello")
