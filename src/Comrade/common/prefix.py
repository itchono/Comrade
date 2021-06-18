import discord
from discord.ext import commands
from common.config import cfg
from common.mongodb import collection

# Prefix for the bot


async def bot_prefix(bot: commands.Bot, message: discord.Message):
    '''
    Returns bot prefix for a specific locale
    '''
    locale = message.guild.id if message.guild else message.author.id

    if (settings := collection(
            "servers").find_one(locale)) and "prefix" in settings:
        return commands.when_mentioned_or(settings["prefix"])(bot, message)
    else:
        return commands.when_mentioned_or(
            cfg["Settings"]["prefix"].strip("\""))(bot, message)


def setup(bot):
    # Entry point for extension
    pass
