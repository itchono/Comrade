from dis_snek.models.snek import Scale, slash_command, InteractionContext
from dis_snek import Snake
from dis_snek.client.const import __version__
from dis_snek.models.discord import Embed
import datetime
import dis_snek

from logger import log


class Telemetry(Scale):
    @slash_command(name="status",
                   description="Gets the status of the bot",
                   scopes=[419214713252216848, 709954286376976425])
    async def status(self, ctx: InteractionContext):
        bot: Snake = ctx.bot

        embed = Embed(title="Comrade Requiem Status")
        embed.set_author(name=bot.user.username, icon_url=bot.user.avatar.url)

        # calculate the time difference between now and start_time
        uptime = datetime.datetime.now() - bot.start_time

        # express the time difference in a human readable format
        uptime_str = str(datetime.timedelta(seconds=uptime.total_seconds()))
        embed.add_field(name="Uptime", value=uptime_str)

        embed.add_field(name="Latency", value=f"{bot.latency * 1000:.2f}ms")
        embed.add_field(name="Library Version", value=__version__)
      
        await ctx.send(embed=embed)


def setup(bot):
    Telemetry(bot)
    log.info("Module telemetry.py loaded.")
