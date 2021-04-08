from discord.ext import commands
from discord_slash import SlashContext
from discord_slash import cog_ext
from discord_slash.utils import manage_commands
from discord.ext.commands.view import StringView
from utils.utilities import bot_prefix

guild_ids = [419214713252216848, 709954286376976425]


class Slash(commands.Cog):
    '''
    Slash commands for Discord
    '''
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="hi",
                        description="just says hello",
                        guild_ids=guild_ids)
    async def hi(self, ctx: SlashContext):
        await ctx.send(content="hello", hidden=True)

    @cog_ext.cog_slash(name="invoke", options=[manage_commands.create_option(
                        name = "command",
                        description = "command to invoke",
                        option_type = 3,
                        required = True
                    )], description="Invoke a command like usual, but now with a slash!",guild_ids=guild_ids)
    async def invoke(self, ctx: SlashContext, command):
        view = StringView(command)
        m = await ctx.send(f"Invoking command `{command}`...")
        ctx = commands.Context(
            prefix=bot_prefix, view=view, bot=self.bot, message=m)
        invoker = view.get_word()
        ctx.invoked_with = invoker

        if command := self.bot.all_commands.get(invoker):
            # invoke a command
            ctx.command = command
            await self.bot.invoke(ctx)

    @cog_ext.cog_slash(name="userinfo", options=[manage_commands.create_option(
                        name = "user",
                        description = "User to get info on",
                        option_type = 6,
                        required = False
                    )], description="Displays info about yourself or another user", guild_ids=guild_ids)
    async def userinfo(self, ctx: SlashContext, user=None):
        command = self.bot.get_command("userinfo")
        await command(ctx, member=user)
