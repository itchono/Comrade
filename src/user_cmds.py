from utils.utilities import *
from utils.mongo_interface import *

class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def avatar(self, ctx, target):
        '''
        Displays the avatar of a target user.
        Made by Slyflare, PhtephenLuu, itchono
        '''
        if u:= await extractUser(self.bot, ctx, target):
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
        # error case triggers automatically.

    @commands.command()
    async def userinfo(self, ctx, target):
        '''
        Displays User Information of said person
        Made by Slyflare, upgraded by itchono
        '''
 
        if member:= await extractUser(self.bot, ctx, target):
            if ctx.guild:
                e = discord.Embed(title="{}".format(member.display_name), colour=member.colour)

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
    
    @commands.command()
    async def rolluser(self, ctx: commands.context):
        '''
        Roles a random ulcer, based on relative weights stored in user configuration file.

        '''
        pool = []

        await ctx.channel.trigger_typing()

        for member in ctx.guild.members:
            weight = getUser(member.id)["daily weight"]
            if not member.bot:
                pool += [member for i in range(weight)]

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