import discord
from discord.ext import commands
from config import cfg
from pretty_help import PrettyHelp
from utils.logger import logger
from utils.checks import isNotThreat
import time

# Map prefixes
if cfg["Settings"]["secondary-prefix"]:
    prefixes = commands.when_mentioned_or(
        cfg["Settings"]["prefix"].strip("\""),
        cfg["Settings"]["secondary-prefix"].strip("\""))
else:
    prefixes = commands.when_mentioned_or(
        cfg["Settings"]["prefix"].strip("\""))

intents = discord.Intents.all()

client = commands.Bot(
    command_prefix=prefixes,
    case_insensitive=True,
    help_command=PrettyHelp(
        no_category="Help Command",
        color=discord.Colour.from_rgb(
            215,
            52,
            42),
        sort_commands=False),
    intents=intents,
    status=discord.Status.online,
    activity=discord.Game(cfg["Settings"]["Status"]))


# Listeners for client events
@client.event
async def on_error(event, *args, **kwargs):
    logger.exception("Discord Error", exc_info=event)


@client.event
async def on_command_error(ctx: commands.Context, exception):
    # When a command fails to execute
    await ctx.send(f"Error: {exception}")
    logger.exception("Command Error", exc_info=exception)


@client.before_invoke
async def set_before_command(ctx: commands.Context):
    ctx.comrade_invoke_t = time.perf_counter()


@client.after_invoke
async def log_after_command(ctx: commands.Context):
    time_taken_ms = (time.perf_counter() - ctx.comrade_invoke_t)*1000
    logger.debug(
        f"Invoked command {ctx.command} in ({round(time_taken_ms, 2)} ms) at {ctx.message.jump_url}")


# Users with threat level 3 or higher cannot use Comrade's features
@client.check_once
async def globalcheck(ctx): return isNotThreat(3)
