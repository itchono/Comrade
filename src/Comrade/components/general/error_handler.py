from discord.ext import commands

from utils.logger import logger


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_error(event, *args, **kwargs):
        logger.exception(event)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, exception):
        # When a command fails to execute
        await ctx.send(f"Error: {exception}")
        try:
            raise exception
        except Exception:
            logger.exception("Command Error")
