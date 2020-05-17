from utils.utilities import *
from utils.mongo_interface import *

class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RND_USER = []
        self.RND_USER_T = datetime.datetime(2000, 1, 1) #stored as UTC
        self._last_member = None

    @commands.command()
    @commands.check(isServer)
    async def avatar(self, ctx:commands.Context, target):
        '''
        Displays the avatar of a target user.
        Made by Slyflare, PhtephenLuu, itchono
        '''
        if u := await extractUser(self.bot, ctx, target):
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
    @commands.check(isServer)
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

                u = getUser(member.id, ctx.guild.id)
                print(u)
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
                u = getUser(member.id, ctx.guild.id)
                for c in u:
                    if c != "_id":
                        e.add_field(name=c, value=u[c], inline=True)

                await ctx.send(embed=e)

    '''
    Random User Functions
    '''

    @commands.command()
    @commands.check(isServer)
    async def rolluser(self, ctx: commands.context):
        '''
        Roles a random ulcer, based on relative weights stored in user configuration file.

        '''
        await ctx.channel.trigger_typing()

        '''
        refresh pool
        '''
        pool = []

        if (datetime.datetime.utcnow() - self.RND_USER_T > datetime.timedelta(hours = 1)):
            # rebuilding cache
            print("Rebuild cache")
            for member in ctx.guild.members:
                weight = getUser(member.id, ctx.guild.id)["daily weight"]
                if not member.bot:
                    pool += [member for i in range(weight)]
            self.RND_USER = pool[:]
            self.RND_USER_T = datetime.datetime.utcnow()

        else:
            pool = self.RND_USER[:]

        random.shuffle(pool)
        luckyperson = pool.pop()
        await self.userinfo(ctx, getUser(luckyperson.id, ctx.guild.id)["nickname"])

    @commands.command()
    @commands.check(isServer)
    async def addUser(self, ctx, username, avatar_url):
        '''
        Adds custom user to database, which can be mentioned.
        '''
        addCustomUser(username, avatar_url, ctx.guild.id)

        e =  self.bot.get_cog('Echo')

        await e.echo(ctx, "I have been added.", username)    

    @commands.command()
    @commands.check(isServer)
    async def listCustomUsers(self, ctx: commands.Context):
        '''
        Lists all custom users
        '''
        u = customUserQuery({"server":ctx.guild.id}) # all custom users