from dis_snek.models.snek import (Scale, slash_command, InteractionContext,
                                  slash_option, OptionTypes)
from dis_snek import Snake
from dis_snek.client.const import __version__, __py_version__
from dis_snek.models.discord import Embed, File
from dis_snek.ext.paginators import Paginator
from custom_client import CommandExecInfo
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
            value=f"{days}d, {hours}h, {minutes}m, {seconds}s",
            inline=True)

        embed.add_field(name="Latency", value=f"{bot.latency * 1000:.2f} "
                        f"ms (curr) / {bot.latency * 1000:.2f} ms (avg)",
                        inline=True)
        embed.add_field(name="Library Version", value=__version__,
                        inline=False)
        embed.add_field(name="Python Version", value=__py_version__,
                        inline=True)
      
        await ctx.send(embed=embed)
        
    @slash_command(name="view_log",
                   description="Gets the log for the bot",
                   scopes=[419214713252216848, 709954286376976425])
    async def viewlog(self, ctx: InteractionContext):
        log_file = File("comrade.log", file_name="comrade_log.txt")
        await ctx.send(file=log_file, ephemeral=True)
        
    @slash_command(name="history",
                   description="Gets command history in this channel",
                   scopes=[419214713252216848, 709954286376976425])
    async def history(self, ctx: InteractionContext):
        logs = self.bot.audit_log[ctx.guild_id][ctx.channel.id]
        if not logs:
            await ctx.send("No command history found in this channel.")
            return
        embed_list = []
        
        execinfo: CommandExecInfo
        for count, execinfo in enumerate(logs, start=1):
            e = Embed(title=f"({count}/{len(logs)}): {execinfo.command_name}",
                      description=f"Arguments: `{execinfo.args}`\nKeyword Args: `{execinfo.kwargs}`",
                      timestamp = execinfo.time.timestamp())
            executor = await ctx.bot.get_member(execinfo.author_id, ctx.guild_id)
            e.set_author(name=executor.display_name, icon_url=executor.avatar.url)
            embed_list.append(e)
            e.set_footer(text=f"Last 10 commands executed in this channel")
            
        paginator = Paginator.create_from_embeds(ctx.bot, *embed_list, timeout=120)
        await paginator.send(ctx)
    
        
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
