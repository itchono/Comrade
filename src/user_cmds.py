from utils.utilities import *
from utils.mongo_interface import *

class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RND_USER = {} # Cache of users for daily roll, per server
        self._last_member = None

    @commands.command()
    async def avatar(self, ctx:commands.Context, *, target=None):
        '''
        Displays the avatar of a target user, self by default
        Made by Slyflare, PhtephenLuu, itchono
        '''
        if not target:
            target = ctx.author.mention

        if u := await extractUser(ctx, target):
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
    async def userinfo(self, ctx, *, target=None):
        '''
        Displays User Information of said person
        Made by Slyflare, upgraded by itchono
        '''
        if not target:
            target = ctx.author.mention

        target = target.strip("\"")

        if ctx.guild and (custom := getCustomUser(target, ctx.guild.id)):
            e = discord.Embed(title="{} (Custom User)".format(target))
            e.set_author(name=f"User Info - {target}")
            e.set_thumbnail(url=custom["url"])
            e.set_footer(icon_url=custom["url"])

            await ctx.send(embed=e)
 
        elif member := await extractUser(ctx, target):
            if ctx.guild:
                e = discord.Embed(title="{}".format(member.display_name), colour=member.colour)
                e.set_author(name=f"User Info - {member}")
                e.set_thumbnail(url=member.avatar_url)
                e.set_footer(icon_url=ctx.author.avatar_url)
                roles = [role for role in member.roles]

                u = getUser(member.id, ctx.guild.id)

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
                
                e.add_field(name="No info available", value="Comrade is in a DM environment, and therefore has no information stored. Try calling this in a server with Comrade set up.", inline=True)

                await ctx.send(embed=e)

    '''
    Random User Functions
    '''
    def rebuildUserCache(self):
        '''
        Rebuilds the random user cache for all servers.
        '''
        self.RND_USER = {}

        for g in self.bot.guilds:
            self.RND_USER[g.id] = []
            for member in g.members:
                weight = getUser(member.id, g.id)["daily weight"]
                if not member.bot: self.RND_USER[g.id] += [member for i in range(weight)]
            
            # special case: list is empty
            if self.RND_USER[g.id] == []:
                for member in g.members:
                    d = getUser(member.id, g.id)
                    d["daily weight"] = 2
                    updateUser(d)
                print("Refilled daily count for {}".format(g))
        print("User Cache Built Successfully.")

    @commands.command()
    @commands.check(isServer)
    async def rollUser(self, ctx: commands.Context):
        '''
        Roles a random ulcer, based on relative weights stored in user configuration file.

        '''
        await ctx.channel.trigger_typing()

        pool = self.RND_USER[ctx.guild.id][:]

        random.shuffle(pool)
        luckyperson = pool.pop()
        await self.userinfo(ctx, target=getUser(luckyperson.id, ctx.guild.id)["nickname"])

    @commands.command()
    @commands.check(isServer)
    async def addCustomUser(self, ctx, username, avatar_url):
        '''
        Adds custom user to database, which can be mentioned.
        '''
        u = ({"name": username, "url": avatar_url, "server": ctx.guild.id})
        updateCustomUser(u)

        e =  self.bot.get_cog('Echo')
        await e.echo(ctx, "I have been added.", username)    

    @commands.command()
    @commands.check(isServer)
    @commands.check(isOP)
    async def editCustomUser(self, ctx, username, field, value):
        '''
        Edits a custom user's fields
        '''
        u = getCustomUser(username, ctx.guild.id)

        if not value:
            try:
                del u[field]
                updateCustomUser(u)
                await delSend("User config value deleted.", ctx.channel)
            except:
                await delSend("Value was not found.", ctx.channel)
        
        else:
            u[field] = value
            updateCustomUser(u)
            await reactOK(ctx)
    
    @commands.command()
    @commands.check(isServer)
    @commands.check(isOP)
    async def removeCustomUser(self, ctx, username):
        '''
        Edits a custom user's fields
        '''
        removeCustomUser(username, ctx.guild.id)
        await reactOK(ctx)

    @commands.command()
    @commands.check(isServer)
    async def listCustomUsers(self, ctx: commands.Context):
        '''
        Lists all custom users
        '''
        u = customUserQuery({"server":ctx.guild.id}) # all custom users

        s = "```Custom Users in {}".format(ctx.guild.name)

        for usr in u:
            s += "\n" + usr["name"]
        
        s += "```"

        await ctx.send(s)
    
    @commands.Cog.listener()
    async def on_ready(self):
        '''
        When bot is loaded, rebuild the cache.
        '''
        self.rebuildUserCache()

    