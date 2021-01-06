import discord
from discord.ext import commands
import typing
import random

from utils.echo import echo, mimic
from utils.checks import isNotThreat
from utils.utilities import is_url

from config import cfg


class Echo(commands.Cog):
    '''
    Send messages as another person, pretend to be someone else
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(isNotThreat())
    @commands.guild_only()
    async def echo(self, ctx: commands.Context,
                   member: typing.Optional[discord.Member] = None,
                   *, text: str):
        '''
        Echoes a block of text as if it were sent by another server member.
        Defaults to self if no member specified.

        Ex. $c echo itchono HELLO THERE SIR
        >>> Itchono: `HELLO THERE SIR`
        '''
        if not member:
            member = ctx.author

        await echo(ctx, member=member,
                   content=text,
                   file=ctx.message.attachments[0] if ctx.message.attachments else None,
                   embed=ctx.message.embeds[0] if ctx.message.embeds else None)
        # await log(ctx.guild, f"Echo for {target.mention} sent by
        # {ctx.author.mention}")
        await ctx.message.delete()

    @commands.command()
    @commands.check(isNotThreat())
    @commands.guild_only()
    async def reverb(self, ctx: commands.Context, message: discord.Message):
        '''
        Copies a message from somewhere into here using echo.
        '''
        await mimic(ctx.channel,
                    content=message.content,
                    username=message.author.display_name,
                    avatar_url=message.author.avatar_url,
                    file=await message.attachments[0].to_file() if message.attachments else None,
                    embed=message.embeds[0] if message.embeds else None)

    @commands.command()
    @commands.check(isNotThreat())
    @commands.guild_only()
    async def cosplay(self, ctx: commands.Context, name: str,
                      img_url: typing.Optional[str] = None, *, message):
        '''
        Sends a message with a custom avatar name and image URL.
        Alternatively, you can also attach an image.

        ex. $c cosplay Giorno Giovanna http://<image> I HAVE A DREAM
        '''
        url = None
        if is_url(img_url):
            url = img_url
        elif ctx.message.attachments:
            url = ctx.message.attachments[0].url
        else:
            message = url + message

        message = " ".join(message)
        await mimic(ctx.channel,
                    content=message, username=name, avatar_url=url)

        await ctx.message.delete()

    @commands.command()
    @commands.check(isNotThreat())
    @commands.guild_only()
    async def everyonesays(self, ctx: commands.Context,
                           count: typing.Optional[int] = 5, *, text: str):
        '''
        Says something a lot of times.
        '''
        humans = [m for m in ctx.guild.members if not m.bot]

        if count > int(cfg["Performance"]["everyonesays-limit"]):
            await ctx.send(ctx,
                           f"That's too many members! Limit is {cfg['Performance']['everyonesays-limit']}")
        else:
            for m in random.sample(humans, count):
                await echo(ctx, content=text, member=m)
