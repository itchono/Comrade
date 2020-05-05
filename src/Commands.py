import discord # core to bot
from discord.ext import commands
import asyncio

from MongoInterface import *

class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def memeapproved(self, ctx:commands.Context):
        msg = await ctx.send("Meme Approved")
        await asyncio.sleep(10)
        await msg.add_reaction("🗑️")

    @commands.command()
    async def getuser(self, ctx, userID):
        userID = eval(userID)
        msg = await ctx.send("{}".format(getUser(userID)))
        await asyncio.sleep(10)
        await msg.add_reaction("🗑️")


    @commands.command()
    async def buymefood(self, ctx:commands.Context):
        msg = await ctx.send("Enter Your Credit Card Info:")
        await asyncio.sleep(10)
        await msg.add_reaction("🗑️")

    @commands.command()
    async def updateUsers(self, ctx:commands.Context):

        for user in ctx.guild.members:
            updateUser({"_id":user.id, "name":user.name})

        await ctx.send("user updating complete")
    
    