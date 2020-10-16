import discord
from discord.ext import commands
from utils import *

import random, typing

class Users(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.WEIGHTED_RND_USER = {} # Cache of users for daily roll, per server
        self.UNWEIGHTED_RND_USER = {} # Cache of users for standard rolling
        
    @commands.command()
    async def avatar(self, ctx:commands.Context, *, member:typing.Union[discord.Member, discord.User]=None):
        '''
        Displays the avatar of a target user, self by default
        Made by Slyflare, PhtephenLuu, itchono
        '''
        if not member: member = ctx.author

        if type(member) == discord.Member:
            # server environment
            a = discord.Embed(color=member.colour, 
                            title="{}'s Avatar".format(member.display_name),
                            url=str(member.avatar_url_as(static_format="png")))
            a.set_image(url='{}'.format(member.avatar_url))
            await ctx.send(embed=a)
        else:
            a = discord.Embed(color=discord.Color.dark_blue(), 
                                title="{}'s Avatar".format(member.name),
                                url=str(member.avatar_url_as(static_format="png")))
            a.set_image(url='{}'.format(member.avatar_url))
            await ctx.send(embed=a)

    @commands.group(invoke_without_command=True)
    async def userinfo(self, ctx: commands.Context, *, member:typing.Union[discord.Member, discord.User] = None):
        '''
        Displays User Information of said person
        Made by Slyflare, upgraded by itchono
        '''
        if not member: member = ctx.author

        e = discord.Embed(title="Info for {}".format(member.display_name), colour=member.colour)
        e.set_author(name=f"User Info - {member}")
        e.set_thumbnail(url=member.avatar_url)
        e.set_footer(icon_url=ctx.author.avatar_url)

        if ctx.guild:

            roles = [role for role in member.roles]

            u = DBuser(member.id, ctx.guild.id)

            for c in u:
                if c == "daily-weight": e.add_field(name=c, value=u[c], inline=True)
            
            e.add_field(name=f"Roles: ({len(roles)})", value=" ".join([role.mention for role in member.roles]))
            try: e.add_field(name="Joined Server", value=f"{member.joined_at.strftime('%B %m %Y at %I:%M:%S %p %Z')}")
            except: pass
            e.add_field(name="Account Created", value=member.created_at.strftime('%B %m %Y at %I:%M:%S %p %Z'))
        
        else:
            e.add_field(name="Account Created", value=member.created_at.strftime('%B %m %Y at %I:%M:%S %p %Z'))
            e.add_field(name="No more info available", value="Comrade is in a DM environment, and therefore has no information stored. Try calling this in a server with Comrade set up.", inline=True)


        await ctx.send(embed=e)

    @userinfo.command()
    async def full(self, ctx: commands.Context, *, member:typing.Union[discord.Member, discord.User] = None):
        '''
        More detailed user info
        '''
        if not member: member = ctx.author

        e = discord.Embed(title="Info for {}".format(member.display_name), colour=member.colour)
        e.set_author(name=f"User Info - {member}")
        e.set_thumbnail(url=member.avatar_url)
        e.set_footer(icon_url=ctx.author.avatar_url)

        if ctx.guild:

            roles = [role for role in member.roles]

            u = DBuser(member.id, ctx.guild.id)

            for c in u:
                if c != "_id": e.add_field(name=c, value=u[c], inline=True)
            
            e.add_field(name=f"Roles: ({len(roles)})", value=" ".join([role.mention for role in member.roles]))
            try: e.add_field(name="Joined Server", value=f"{member.joined_at.strftime('%B %m %Y at %I:%M:%S %p %Z')}")
            except: pass
            e.add_field(name="Account Created", value=member.created_at.strftime('%B %m %Y at %I:%M:%S %p %Z'))
        
        else:
            e.add_field(name="Account Created", value=member.created_at.strftime('%B %m %Y at %I:%M:%S %p %Z'))
            e.add_field(name="No more info available", value="Comrade is in a DM environment, and therefore has no information stored. Try calling this in a server with Comrade set up.", inline=True)

        await ctx.send(embed=e)

            
    '''
    Random User Functions
    '''
    async def rebuildcache(self, g):
        '''
        Rebuilds the random user cache for a given server.
        '''
        self.WEIGHTED_RND_USER[g.id] = []
        self.UNWEIGHTED_RND_USER[g.id] = []
        
        for member in g.members:
            if u := DBuser(member.id, g.id): pass
            else:
                # account for new users
                stp = self.bot.get_cog("Databases")
                updateDBuser(stp.setupuser(member))
                u = DBuser(member.id, g.id)

            weight = u["daily-weight"]
            if not member.bot: 
                self.WEIGHTED_RND_USER[g.id] += [member for i in range(weight)]
                self.UNWEIGHTED_RND_USER[g.id] += [member]
        
        # special case: list is empty
        if self.WEIGHTED_RND_USER[g.id] == []:

            try: daily = DBcfgitem(g.id, "default-daily-count")
            except: daily = 0

            for member in g.members:
                d = DBuser(member.id, g.id)                
                d["daily-weight"] = daily
                updateDBuser(d)

            DAILY_MEMBER_STALENESS = DBcfgitem(g.id, "daily-member-staleness")

            if DAILY_MEMBER_STALENESS >= 0:
                threshold = datetime.datetime.now() - datetime.timedelta(DAILY_MEMBER_STALENESS)
                member_ids = set([i.id for i in g.members])

                for channel in g.text_channels:
                    author_ids = set([i.author.id for i in await channel.history(limit=None,after=threshold).flatten() if i.type == discord.MessageType.default])
                    member_ids -= author_ids

                for i in member_ids:
                    u = DBuser(i, g.id)
                    u["daily-weight"] = 0
                    updateDBuser(u)

            for member in g.members:
                if u := DBuser(member.id, g.id): pass
                else:
                    # account for new users
                    stp = self.bot.get_cog("Databases")
                    updateDBuser(stp.setupuser(member))
                    u = DBuser(member.id, g.id)

                weight = u["daily-weight"]
                if not member.bot: 
                    self.WEIGHTED_RND_USER[g.id] += [member for i in range(weight)]
                    self.UNWEIGHTED_RND_USER[g.id] += [member]

                await log(g, f"Refilled daily count and trimmed users in past {DAILY_MEMBER_STALENESS} days")
        await log(g, f"User Cache built.\nWeighted List -- {len(self.WEIGHTED_RND_USER[g.id])} entries\nUnweighed List -- {len(self.UNWEIGHTED_RND_USER[g.id])} entries")

    @commands.command()
    async def requiem(self, ctx: commands.Context, day: int = 30, trim = False):
        '''
        Generates a list of users who have not talked in the past x days
        '''
        threshold = datetime.datetime.now() - datetime.timedelta(day)

        member_ids = set([i.id for i in ctx.guild.members])

        await ctx.send('Scanning all members. This will take a while')

        for channel in ctx.guild.text_channels:

            author_ids = set([i.author.id for i in await channel.history(limit=None,after=threshold).flatten() if i.type == discord.MessageType.default])

            member_ids -= author_ids

        await ctx.send(f"{len(member_ids)} members detected to have not posted in the past {day} days.")

        OP = isOP(ctx) # check before trimming

        s = "```"
        for i in [await getUser(ctx, str(j)) for j in member_ids]:
            s += i.display_name + "\n"
            
            if trim and OP:
                u = DBuser(i.id, ctx.guild.id)
                u["daily-weight"] = 0
                updateDBuser(u)
        s += "```"
        await ctx.send(s)

        if trim:
            cog = self.bot.get_cog("Users")
            await cog.rebuildcache(ctx.guild)
            await ctx.send("Users above have been removed from the daily member pool.")

    @commands.command()
    @commands.guild_only()
    async def rollUser(self, ctx: commands.Context, weighted=False):
        '''
        Rolls a random user in the server, either weighted or unweighted
        '''
        async with ctx.channel.typing():
            luckyperson = random.choice(self.UNWEIGHTED_RND_USER[ctx.guild.id]) if not weighted else random.choice(self.WEIGHTED_RND_USER[ctx.guild.id])
        await self.userinfo(ctx, member=luckyperson)

    @commands.command()
    @commands.guild_only()
    async def remind(self, ctx:commands.Context, *, member:discord.Member):
        '''
        Makes it so that when a user comes online, you are notified by Comrade
        '''
        d = DBuser(member.id, ctx.guild.id)
        try: 
            d["check-when-online"].remove(ctx.author.id)
            await ctx.send(f"You will no longer be notified by when {member.display_name} changes their status.")
        except:
            d["check-when-online"].append(ctx.author.id)
            await ctx.send(f"You will now be notified by when {member.display_name} changes their status.")
        updateDBuser(d)

    async def on_load(self):
        '''
        When bot is loaded, rebuild the cache.
        '''
        for g in self.bot.guilds: await self.rebuildcache(g)
        print('User Lists ready')

    @commands.command()
    @commands.guild_only()
    async def modchance(self, ctx, member:typing.Optional[discord.Member]=None):
        '''
        Shows the chance of a user to be member of the day [MoD]
        '''

        if not member: member = ctx.author

        total = len(self.WEIGHTED_RND_USER[ctx.guild.id])

        count = self.WEIGHTED_RND_USER[ctx.guild.id].count(member)

        await ctx.send(f"{member.display_name}'s chance of being rolled tomorrow is {count}/{total} ({round(count/total * 100, 2)}%)")


    @commands.command()
    @commands.guild_only()
    async def favcolour(self, ctx, member:typing.Optional[discord.Member]=None, colour=None):
        '''
        Sets a user's favourite colour. 
        TODO: Can be either hex or a common word. If recognized, it will show up in your userinfo command.
        can also view another user's favourite colour
        '''
        if member:
            u = DBuser(member.id, ctx.guild.id)
            await ctx.send(f"{member.display_name}'s favourite colour is {u['favourite-colour']}")
        elif colour:
            u = DBuser(ctx.author.id, ctx.guild.id)
            u["favourite-colour"] = colour
            updateDBuser(u)
            await reactOK(ctx)

        else:
            u = DBuser(ctx.author.id, ctx.guild.id)
            await ctx.send(f"{ctx.author.display_name}'s favourite colour is {u['favourite-colour']}")

