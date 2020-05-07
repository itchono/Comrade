from utils.utilities import *
from utils.mongo_interface import *

import discord
import aiohttp

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def getuser(self, ctx:commands.Context, nickname):
        '''
        Looks up a user based on their server nickname, returning a dictionary with the document entry
        HINT: Use Quotes like this "A user's name" to deal with names containing spaces
        '''
        e = discord.Embed(title="Info for {}".format(nickname))
        u = getUserfromNick(nickname)

        for c in u:
            if c != "_id":
                e.add_field(name=c, value=u[c], inline=True)
        await ctx.send(embed=e)

    @commands.command()
    @commands.check(isnotThreat)
    async def echo(self, ctx:commands.Context, text:str, tgt=None):
        '''
        Echoes a block of text as if it were sent by someone else.
        Defaults to the author of the message is no target is given.
        Can mention by nickname.
        '''

        if not tgt: tgt = ctx.author
        else: tgt = ctx.message.mentions[0]

        webhook = discord.Webhook.partial(707756204969033731, 'fBGEs9CYku6Cs9qbXTfu1HkyycZnR9zQbCbdlL7o3b0ul7xbHArae7B0pBCRMsBfX3Wy', adapter=discord.RequestsWebhookAdapter())
        #webhook.edit()
        webhook.send(text, username=tgt.display_name, avatar_url=tgt.avatar_url)
        await ctx.message.delete()

    @commands.command()
    async def buymefood(self, ctx:commands.Context):
        '''
        Maybe buys you food
        '''
        await delSend("Enter Your Credit Card Info...", ctx.channel)

    @commands.command()
    async def avatar(self, ctx, nickname):
        '''
        Displays the avatar of the said person
        '''
        u = ctx.guild.get_member((getUserfromNick(nickname))["_id"])
        if not u:
            await ctx.send("Member with username " + nickname + " not found.")
        else:
            a = discord.Embed(color = discord.Color.dark_blue(), title="{}'s Avatar".format(u.display_name), url=str(u.avatar_url_as(static_format="png")))
            a.set_image(url='{}'.format(u.avatar_url))
            await ctx.send(embed=a)

    @commands.command()
    async def test_userinfo(self, ctx, member: discord.member = None):
        '''
        testestestesstetstststs
        '''
<<<<<<< HEAD
=======
        member = ctx.author if not member else member
        roles = [role for role in member.roles]
>>>>>>> 441d56e7812b1d733a95c2b96b2791465c4a775d

        embed = discord.Embed(colour = member.color)

        embed.set_author(name=f"User Info - {member}")
        embed.set_thumbnail(url=member.avatar_url)
