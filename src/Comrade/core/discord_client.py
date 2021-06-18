import discord
from discord.ext import commands
from discord_slash import SlashCommand
from common.config import cfg
from common.logger import logger
from common.checks import isNotThreat
from core.comrade_help import ComradeHelp
from common.prefix import bot_prefix
import os

intents = discord.Intents.all()

client = commands.Bot(
    command_prefix=bot_prefix,
    case_insensitive=True,
    help_command=ComradeHelp(),
    intents=intents,
    status=discord.Status.online,
    activity=discord.Game(cfg["Settings"]["Status"]))

slash = SlashCommand(client,
                     override_type=True,
                     sync_commands=True,
                     sync_on_cog_reload=True,
                     delete_from_unused_guilds=True)


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


# Users with threat level 3 or higher cannot use Comrade's features
@client.check_once
async def globalcheck(ctx): return isNotThreat(3)(ctx)
