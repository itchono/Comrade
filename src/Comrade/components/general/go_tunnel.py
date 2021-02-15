# Tunnel to talk with Go Bot
import discord
from discord.ext import commands

from config import cfg
from utils.logger import logger
from db import relay_channel


class Go(commands.Cog):
    '''
    Communicates with Gomrade to serve as a data relay between the two
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel == relay_channel() and message.content.startswith("<%PY>"):
            logger.info(f"Relay message: {message.content}")

    @commands.command()
    async def go(self, ctx: commands.Context, *, message):
        '''
        Sends a message to the go bot
        '''
        await relay_channel().send("<%GO>" + message)
