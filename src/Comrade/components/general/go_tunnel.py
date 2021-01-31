# Tunnel to talk with Go Bot
import discord
from discord.ext import commands

from config import cfg
from utils.logger import logger

GO_ID = int(cfg["Hosting"]["go-id"])


class Go(commands.Cog):
    '''
    Communicates with Gomrade to serve as a data relay between the two
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == GO_ID:
            logger.info(message.content)

    @commands.command()
    async def go(self, ctx: commands.Context, *, message):
        '''
        Sends a message to the go bot
        '''
        gobot: discord.Member = ctx.guild.get_member(GO_ID)
        dmchannel = await gobot.create_dm()
        await dmchannel.send(message)
