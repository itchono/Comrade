import discord
from discord.ext import commands
from utils import *

import asyncio, random, typing

class Echo(commands.Cog):
    def __init__(self, bot): self.bot = bot

    @commands.command()
    @commands.check(isNotThreat())
    @commands.guild_only()
    async def echo(self, ctx: commands.Context, target: typing.Optional[discord.Member] = None, *, text: str):
        '''
        Echoes a block of text as if it were sent by someone else [server member, custom user]
        Can mention people by nickname or user ID too.

        Defaults to self if no user specified. Use \ to escape mentioning names if you want this case.
        
        Ex. $c echo itchono HELLO THERE SIR 
        >>> Impersonates itchono, sending a message with content `HELLO THERE SIR`
        '''
        if not target: target = ctx.author
        await echo(ctx, member=target, content=text, file=ctx.message.file, embed=ctx.message.embed)
        await log(ctx.guild, f"Echo for {target.mention} sent by {ctx.author.mention}")
        await ctx.message.delete()

    @commands.command()
    @commands.check(isNotThreat())
    @commands.guild_only()
    async def everyonesays(self, ctx: commands.Context, text: str, count: int = 0):
        '''
        Says something a lot of times.
        '''
        online_humans = [m for m in ctx.guild.members if (str(m.status) != "offline" and not m.bot)]

        onlinecount = len(online_humans)
        # number of online human members

        if count > onlinecount:
            await delSend(ctx, f"That's too many members! Only {onlinecount} human members are online right now!")
        else:
            if not count: count = 5 if onlinecount >= 5 else onlinecount

            for m in random.sample(online_humans, count): await echo(ctx, content=text, member=m)

            await asyncio.sleep(30)

            if count > 5: await self.cleanwebhooks(ctx)
    
    @commands.command()
    @commands.guild_only()
    async def cleanwebhooks(self, ctx:commands.Context):
        '''
        Deletes echoed messages from Comrade and cleans up Webhooks.
        '''
        for wh in await ctx.channel.webhooks(): await wh.delete()
        await ctx.channel.purge(check=isWebhook, bulk=True)