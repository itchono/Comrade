from utils.utilities import *
from utils.mongo_interface import *

import aiohttp


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def getuser(self, ctx: commands.Context, nickname):
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
    async def echo(self, ctx: commands.Context, text: str, tgt=None, deleteMsg=True):
        '''
        Echoes a block of text as if it were sent by someone else.
        Defaults to the author of the message is no target is given.
        Can mention people by nickname or user ID too.

        Ex. $c echo "HELLO THERE SIR" @itchono
        '''
        u = getCustomUser(tgt)

        if not u:
            u = await extractUser(self.bot, ctx, tgt)

            if not tgt:
                u = ctx.author

            webhook = discord.Webhook.partial(707756204969033731,
                                          'fBGEs9CYku6Cs9qbXTfu1HkyycZnR9zQbCbdlL7o3b0ul7xbHArae7B0pBCRMsBfX3Wy',
                                          adapter=discord.RequestsWebhookAdapter())
            # webhook.edit()
            webhook.send(text, username=u.display_name, avatar_url=u.avatar_url)
            if deleteMsg: await ctx.message.delete()
            
        else:
            webhook = discord.Webhook.partial(707756204969033731,
                                          'fBGEs9CYku6Cs9qbXTfu1HkyycZnR9zQbCbdlL7o3b0ul7xbHArae7B0pBCRMsBfX3Wy',
                                          adapter=discord.RequestsWebhookAdapter())
            # webhook.edit()
            webhook.send(text, username=u["name"], avatar_url=u["url"])
            if deleteMsg: await ctx.message.delete()

    @commands.command()
    @commands.check(isnotThreat)
    async def everyonesays(self, ctx: commands.Context, text: str, count: int = 5):
        '''
        Please don't use this oh god
        '''
        onlinecount = 0

        for member in ctx.guild.members:
            if str(member.status) != "offline":
                onlinecount += 1

        if count > onlinecount/2:
            await delSend("Are you fucking serious", ctx.channel)
        else:
            mems = list(ctx.guild.members)
            random.shuffle(mems)

            for member in mems:
                await self.echo(ctx, text, member.display_name, False)
                count -= 1
                if count <= 0: break

            await asyncio.sleep(30)

            if count > 5:
                await self.cleanwebhooks(ctx)

    @commands.command()
    async def cleanwebhooks(self, ctx:commands.Context):
        '''
        Deletes echoed messages from Comrade
        '''
        await ctx.channel.purge(check=isWebhook, bulk=True)

    @commands.command()
    async def clearcommands(self, ctx:commands.Context):
        '''
        Cleans up commands from sent from users in a channel.
        '''
        await ctx.channel.purge(check=isCommand, bulk=True)

    @commands.command()
    async def buymefood(self, ctx: commands.Context):
        '''
        Maybe buys you food
        '''
        await delSend("Enter Your Credit Card Info...", ctx.channel)

    @commands.command()
    async def dmUser(self, ctx: commands.Context, nickname):
        '''
        DM given user
        Made by vdoubleu
        '''

        await delSend("dm user in progress...", ctx.channel)
        
        if not (getUserfromNick(nickname)):
            await ctx.send("Member with username " + nickname + " not found.")
        else:
            userId = (getUserfromNick(nickname))["_id"]
            user = ctx.guild.get_member(userId)
            
            await DM("hello", user)

            await delSend("I have sent a dm to that person", ctx.channel)

    @commands.command()
    async def avatar(self, ctx, tgt):
        '''
        Displays the avatar of the said person
        Made by Slyflare, PhtephenLuu, itchono
        '''
        u = await extractUser(self.bot, ctx, tgt)

        if u:
            if ctx.guild:
                # server environment
                a = discord.Embed(color=discord.Color.dark_blue(), 
                                title="{}'s Avatar".format(u.display_name),
                                url=str(u.avatar_url_as(static_format="png")))
                a.set_image(url='{}'.format(u.avatar_url))
                await ctx.send(embed=a)
            else:
                a = discord.Embed(color=discord.Color.dark_blue(), 
                                    title="{}'s Avatar".format(u.name),
                                    url=str(u.avatar_url_as(static_format="png")))
                a.set_image(url='{}'.format(u.avatar_url))
                await ctx.send(embed=a)

    @commands.command()
    async def rolluser(self, ctx: commands.context):
        '''
        Roles a random ulcer, based on relative weights stored in user configuration file.

        '''
        pool = []

        for member in ctx.guild.members:
            weight = getUser(member.id)["daily weight"]
            if not member.bot:
                pool += [member for i in range(weight)]

        print(pool)

        random.shuffle(pool)

        luckyperson = pool.pop()

        await self.userinfo(ctx, getUser(luckyperson.id)["nickname"])

    @commands.command()
    async def addUser(self, ctx, username, avatar_url):
        '''
        Adds custom user to database, which can be mentioned.
        '''
        addCustomUser(username, avatar_url)
        await self.echo(ctx, "I have been added.", username)

    @commands.command()
    async def msgInfo(self, ctx, msgid):
        msg = await ctx.channel.fetch_message(msgid)

        await ctx.send("Author: {}".format(msg.author))

    @commands.command()
    async def userinfo(self, ctx, tgt):
        '''
        Displays User Information of said person
        Made by Slyflare, upgraded by itchono
        '''
        member = await extractUser(self.bot, ctx, tgt)

        if member:

            if ctx.guild:

                e = discord.Embed(title="Info for {}".format(member.display_name), colour=member.colour)

                e.set_author(name=f"User Info - {member}")
                e.set_thumbnail(url=member.avatar_url)
                e.set_footer(icon_url=ctx.author.avatar_url)
                roles = [role for role in member.roles]

                u = getUser(member.id)
                for c in u:
                    if c != "_id":
                        e.add_field(name=c, value=u[c], inline=True)
                e.add_field(name=f"Roles: ({len(roles)})", value=" ".join([role.mention for role in member.roles]))

                await ctx.send(embed=e)

            else:
                e = discord.Embed(title="Info for {}".format(member.name))

                e.set_author(name=f"User Info - {member}")
                e.set_thumbnail(url=member.avatar_url)
                e.set_footer(icon_url=ctx.author.avatar_url)
                u = getUser(member.id)
                for c in u:
                    if c != "_id":
                        e.add_field(name=c, value=u[c], inline=True)

                await ctx.send(embed=e)

