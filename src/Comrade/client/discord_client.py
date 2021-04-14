import discord
from discord.ext import commands
from discord_slash import SlashCommand
from config import cfg
from utils.logger import logger
from utils.checks import isNotThreat
from utils.comrade_help import ComradeHelp
import time
import os

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
    help_command=ComradeHelp(),
    intents=intents,
    status=discord.Status.online,
    activity=discord.Game(cfg["Settings"]["Status"]))

slash = SlashCommand(client, override_type=True, sync_commands=True, sync_on_cog_reload=True, delete_from_unused_guilds=True)


# Listeners for client events
@client.event
async def on_error(event, *args, **kwargs):
    try:
        raise event
    except discord.HTTPException:
        os.system("kill 1")  # hard restart on 429
    except Exception:
        logger.exception(event)


@client.event
async def on_command_error(ctx: commands.Context, exception):
    # When a command fails to execute
    await ctx.send(f"Error: {exception}", reference=ctx.message)
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
async def globalcheck(ctx): return isNotThreat(3)(ctx)
