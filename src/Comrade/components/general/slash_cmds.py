from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash import SlashContext
from discord_slash import cog_ext
from discord_slash.utils import manage_commands

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

    @cog_ext.cog_slash(name="test",
                        description="just says hello",
                        guild_ids=guild_ids)
    async def _test(self, ctx: SlashContext):
        await ctx.send(content="hello")

    @cog_ext.cog_slash(name="invoke", options=[manage_commands.create_option(
                        name = "command",
                        description = "command to invoke",
                        option_type = 3,
                        required = True
                    )],guild_ids=guild_ids)
    async def invoke(self, ctx: SlashContext, command):
        msgctx = await self.bot.get_context(ctx.channel.last_message)
        await self.bot.get_command(command)(msgctx)
        ctx.send("did a command send")
