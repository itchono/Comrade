from dis_snek.models.snek import (Scale, slash_command, InteractionContext,
                                  slash_option, OptionTypes)
from dis_snek import Snake
from dis_snek.client.const import __version__, __py_version__
from dis_snek.models.discord import Embed
import datetime
from inspect import signature

from logger import log


class Telemetry(Scale):
    @slash_command(name="status",
                   description="Gets the status of the bot",
                   scopes=[419214713252216848, 709954286376976425])
    async def status(self, ctx: InteractionContext):
        bot: Snake = ctx.bot

        embed = Embed(title="Comrade Requiem Status",
                      color=0xD7342A)
        embed.set_author(name=bot.user.username, icon_url=bot.user.avatar.url)

        # calculate the time difference between now and start_time
        uptime = datetime.datetime.now() - bot.start_time

        # express the time difference in a human readable format
        days = uptime.days
        (hours, seconds) = divmod(uptime.seconds, 3600)
        (minutes, seconds) = divmod(seconds, 60)
        
        embed.add_field(
            name="Uptime",
            value=f"{days}d, {hours}h, {minutes}m, {seconds}s")

        embed.add_field(name="Latency", value=f"{bot.latency * 1000:.2f}ms")
        embed.add_field(name="Library Version", value=__version__)
        embed.add_field(name="Python Version", value=__py_version__)
      
        await ctx.send(embed=embed)
        
    @slash_command(name="all_commands",
                   description="returns all registered commands in this scope",
                   scopes=[419214713252216848, 709954286376976425])
    async def all_commands(self, ctx: InteractionContext):
        interaction_names = [
            str(interaction) for interaction in ctx.bot.interactions[ctx.guild_id].keys()]
        await ctx.send("```" + '\n'.join(interaction_names) + "```")
        
    @slash_command(name="inspect_command",
                   description="Inspects the function signature of a slash command",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="command", description="The command to inspect",
                  opt_type=OptionTypes.STRING, required=True)
    async def inspect(self, ctx: InteractionContext, command: str):
        if cmd := ctx.bot.interactions[ctx.guild_id][command]:
            await ctx.send(f"{command} has signature {signature(cmd.callback)}")
        else:
            await ctx.send(f"Command {command} not found.")

def setup(bot):
    Telemetry(bot)
    log.info("Module telemetry.py loaded.")
