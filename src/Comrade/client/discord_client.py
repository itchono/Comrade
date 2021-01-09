import discord
from discord.ext import commands
from config import cfg
from pretty_help import PrettyHelp
from utils.logger import logger

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
    intents=intents)


@client.event
async def on_error(event, *args, **kwargs):
    try:
        raise event
    except Exception:
        logger.exception(event)
