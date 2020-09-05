import discord
from discord.ext import commands
from cfg import *

prefixes = (BOT_PREFIX, SECONDARY_PREFIX) if SECONDARY_PREFIX else (BOT_PREFIX,)

# Bot Client
client = commands.Bot(command_prefix=prefixes, case_insensitive=True,
                      help_command=commands.MinimalHelpCommand(
                          no_category="Help Command"))