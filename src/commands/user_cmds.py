from utils.utilities import *
from utils.mongo_interface import *

class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.WEIGHTED_RND_USER = {} # Cache of users for daily roll, per server
        self.UNWEIGHTED_RND_USER = {} # Cache of users for standard rolling
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
    async def userinfo(self, ctx: commands.Context, *, target=None):
        '''
        Displays User Information of said person
        Made by Slyflare, upgraded by itchono
        '''
        if not target:
            target = ctx.author.mention

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
    async def rebuildUserCache(self, g):
        '''
        Rebuilds the random user cache for a given server.
        '''
        self.WEIGHTED_RND_USER[g.id] = []
        self.UNWEIGHTED_RND_USER[g.id] = []
        
        for member in g.members:
            if u := getUser(member.id, g.id): pass
            else:
                # account for new users
                stp = self.bot.get_cog("Setup")
                updateUser(stp.setupuser(member))
                u = getUser(member.id, g.id)

            weight = u["daily weight"]
            if not member.bot: 
                self.WEIGHTED_RND_USER[g.id] += [member for i in range(weight)]
                self.UNWEIGHTED_RND_USER[g.id] += [member]
        
        # special case: list is empty
        if self.WEIGHTED_RND_USER[g.id] == []:
            for member in g.members:
                d = getUser(member.id, g.id)
                d["daily weight"] = 2
                updateUser(d)

            if DAILY_MEMBER_STALENESS >= 0:
                threshold = datetime.datetime.now() - datetime.timedelta(DAILY_MEMBER_STALENESS)
                member_ids = set([i.id for i in g.members])

                for channel in g.text_channels:
                    author_ids = set([i.author.id for i in await channel.history(limit=None,after=threshold).flatten()])
                    member_ids -= author_ids

                for i in member_ids:
                    u = getUser(i, g.id)
                    u["daily weight"] = 0
                    updateUser(u)

                await log(g, f"Refilled daily count and trimmed users in past {DAILY_MEMBER_STALENESS} days")
        await log(g, "User Cache Built Successfully.")

    @commands.command()
    async def requiem(self, ctx: commands.Context, day: int = 30, trim = False):
        '''
        Generates a list of users who have not talked in the past x days
        '''
        threshold = datetime.datetime.now() - datetime.timedelta(day)

        member_ids = set([i.id for i in ctx.guild.members])

        await ctx.send('Scanning all members. This will take a while')

        for channel in ctx.guild.text_channels:

            author_ids = set([i.author.id for i in await channel.history(limit=None,after=threshold).flatten()])
            member_ids -= author_ids

        await ctx.send(f"{len(member_ids)} members detected to have not posted in the past {day} days.")

        OP = isOP(ctx) # check before trimming

        s = "```"
        for i in [await extractUser(ctx, str(j)) for j in member_ids]:
            s += i.display_name + "\n"
            
            if trim and OP:
                u = getUser(i.id, ctx.guild.id)
                u["daily weight"] = 0
                updateUser(u)
        s += "```"
        await ctx.send(s)

        if trim:
            cog = self.bot.get_cog("Users")
            await cog.rebuildUserCache(ctx.guild)
            await ctx.send("Users above have been removed from the daily member pool.")

    @commands.command()
    @commands.guild_only()
    async def rollUser(self, ctx: commands.Context, weighted=False):
        '''
        Rolls a random user in the server, either weighted or unweighted
        '''
        await ctx.channel.trigger_typing()
        luckyperson = random.choice(self.UNWEIGHTED_RND_USER[ctx.guild.id]) if not weighted else random.choice(self.WEIGHTED_RND_USER[ctx.guild.id])
        await self.userinfo(ctx, target=getUser(luckyperson.id, ctx.guild.id)["nickname"])

    @commands.command()
    @commands.guild_only()
    async def addCustomUser(self, ctx: commands.Context, username, avatar_url):
        '''
        Adds custom user to database, which can be mentioned.
        '''
        e =  self.bot.get_cog('Echo')

        if u := getCustomUser(username, ctx.guild.id): await e.echo(ctx, "Oh hey I'm already here!", username)

        else:
            u = ({"name": username, "url": avatar_url, "server": ctx.guild.id})
            updateCustomUser(u)
            await e.echo(ctx, "I have been added.", username)

    @commands.command()
    @commands.guild_only()
    @commands.check(isOP)
    async def editCustomUser(self, ctx: commands.Context, username, field, value):
        '''
        Edits a custom user's fields
        '''
        u = getCustomUser(username, ctx.guild.id)

        if not value:
            try:
                del u[field]
                updateCustomUser(u)
                await delSend(ctx, "User config value deleted.")
            except:
                await delSend(ctx, "Value was not found.")
        
        else:
            u[field] = value
            updateCustomUser(u)
            await reactOK(ctx)
    
    @commands.command()
    @commands.guild_only()
    @commands.check(isOP)
    async def removeCustomUser(self, ctx: commands.Context, username):
        '''
        Edits a custom user's fields
        '''
        removeCustomUser(username, ctx.guild.id)
        await reactOK(ctx)

    @commands.command()
    @commands.guild_only()
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

    @commands.command()
    async def remind(self, ctx:commands.Context, target:str):
        '''
        Makes it so that when a user comes online, you are notified by Comrade
        '''
        if u := await extractUser(ctx, target):
            d = getUser(u.id, ctx.guild.id)
            try: 
                d["check when online"].remove(ctx.author.id)
                await ctx.send(f"You will no longer be notified by when {u.display_name} changes their status.")
            except:
                d["check when online"].append(ctx.author.id)
                await ctx.send(f"You will now be notified by when {u.display_name} changes their status.")
            updateUser(d)
    
    @commands.Cog.listener()
    async def on_ready(self):
        '''
        When bot is loaded, rebuild the cache.
        '''
        for g in self.bot.guilds:
            await self.rebuildUserCache(g)

    