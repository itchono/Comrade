import discord
from discord.ext import commands

import random
import asyncio

from utils.utilities import role, ufil
from utils.checks import isOP
from db import collection, RELAY_ID


class RandomEvents(commands.Cog):
    '''
    Random event
    '''
    probabilities: dict = {"nameswap": 1, "rickroll": 1, "nothing": 998}

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def nameswap(self, ctx: commands.Context):
        '''
        Changes the nickname of the above person
        '''
        await ctx.send(
            f"__**~NAMESWAP~**__\nThe person above (Current name: {ctx.author.display_name}) will have their name changed to the first thing that the next person below says.",
            delete_after=120)

        def check(m):
            return not m.author.bot and m.content and m.author != ctx.author and m.channel == ctx.channel

        try:
            msg = await self.bot.wait_for('message', check=check, timeout=120)
        except asyncio.TimeoutError:
            await ctx.send("Nameswap aborted (120s timeout).")
            return

        try:
            await ctx.author.edit(nick=msg.content[:32], reason="Comrade name change")
            # Note: must be less than 32 char
            await ctx.send(
                f"{ctx.author.mention}, your name has been changed to `{msg.content}`!")
        except Exception:
            # Mission permissions
            await ctx.send(
                f"{ctx.author.mention}, you must change your name to `{msg.content}`!")

        collection("users").update_one(
                    ufil(ctx.author),
                    {"$set": {
                        "persistent-name":
                        msg.content[:32]}})
        # Lock name

    async def rickroll(self, ctx: commands.Context):
        '''
        Assigns the rick role
        '''
        rickrole = await role(ctx.guild, "Rick")

        for m in rickrole.members:
            # remove bearer of previous rick role
            roles = m.roles
            roles.remove(rickrole)
            await m.edit(roles=roles)

        roles = ctx.author.roles
        roles.append(rickrole)
        await ctx.author.edit(roles=roles)
        await ctx.send(f"{ctx.author.mention} got rick roled.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.guild and message.guild.id != RELAY_ID and \
                collection("servers").find_one(message.guild.id)["jokes"]:
            choice = random.choices(
                *zip(*RandomEvents.probabilities.items()))[0]

            if choice != "nothing":
                ctx = await self.bot.get_context(message)

                if choice == "nameswap":
                    await self.nameswap(ctx)
                elif choice == "rickroll":
                    await self.rickroll(ctx)

    @commands.Cog.listener()
    async def on_member_update(self,
                               before: discord.Member, after: discord.Member):
        if before.nick != after.nick:

            userdoc = collection("users").find_one(ufil(after))

            if "persistent-name" not in userdoc:
                return
            await after.edit(nick=userdoc["persistent-name"], reason="Comrade name change")

    @commands.command()
    @commands.check(isOP())
    async def clearnamelock(self, ctx: commands.Context, member: discord.Member):
        '''
        Clears name lock on a user who got nameswapped
        '''
        collection("users").update_one(
                    ufil(member),
                    {"$unset": {
                        "persistent-name": ""}})

        await ctx.send(f"Name Lock for {member.display_name} has been removed.")

    @commands.command()
    @commands.check(isOP())
    async def induce(self, ctx: commands.Context):
        await self.nameswap(ctx)
