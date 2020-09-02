from utils.utilities import *
from utils.db_utils import *

'''
Comrade - Timed announcements
'''

class Announcements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.announcements = {}

        self.timedannounce.start()

        
    def cog_unload(self):
        self.timedannounce.cancel()

    async def dailyannounce(self, channel: discord.TextChannel, guildid):
        '''
        Daily announcement
        '''
        now = localTime()

        m = await channel.send("Good morning everyone! Today is {}. Have a great day.".format(localTime().strftime("%A, %B %d (Day %j in %Y). It's %I:%M %p %Z")))

        '''
        Daily user
        '''
        cog = self.bot.get_cog("Users")

        ctx = await self.bot.get_context(m)

        active = bool(cog.WEIGHTED_RND_USER[ctx.guild.id])

        choices = cog.WEIGHTED_RND_USER[ctx.guild.id] if active else cog.UNWEIGHTED_RND_USER[ctx.guild.id]
        luckyperson = random.choice(choices)

        d = DBuser(luckyperson.id, guildid)
  
        if active: 
          d["daily-weight"] -= 1
          updateDBuser(d)
          # self regulating; once probability drops to zero, we just need to refill.

        dailyrole = await dailyRole(channel.guild)

        for m in dailyrole.members:
            # remove bearer of previous daily role
            roles = m.roles
            roles.remove(dailyrole)
            await m.edit(roles=roles)
        
        roles = luckyperson.roles
        roles.append(dailyrole)
        await luckyperson.edit(roles=roles)

        await channel.send("Today's Daily Member is **{}**".format(luckyperson.display_name))
        await cog.avatar(ctx, member=luckyperson)
        
        await cog.rebuildcache(channel.guild)

    @tasks.loop(minutes=1.0)
    async def timedannounce(self):
        '''
        Makes an announcement
        '''
        servers = DBfind(SERVERCFG_COL)

        for s in servers:
            now = localTime()
            for a in self.announcements[s["_id"]]:

                if (now.strftime("%H:%M") == a["time"]):
                    c = self.bot.get_channel(s["announcements-channel"])

                    if c:
                        if hasattr(a["announcement"], "__call__"): await a["announcement"](c, s["_id"]) # daily announce
                        else: await c.send(a["announcement"])


    @timedannounce.before_loop
    async def before_timedannounce(self):
        await self.bot.wait_until_ready()

        for g in self.bot.guilds:
            additonal_announcements = [{"server":g.id, "time":"08:00", "announcement":self.dailyannounce, "owner":None}]
            if d := DBfind(ANNOUNCEMENTS_COL, {"server":g.id}): self.announcements[g.id] = d + additonal_announcements
            else: self.announcements[g.id] = additonal_announcements

    @commands.command()
    @commands.guild_only()
    async def addannounce(self, ctx: commands.Context, time, *, message):
        '''
        Adds an announcement to the announcement system [24 hr time].
        Each user is allowed to have a maximum of one announcement.
        '''
        announce = {"server":ctx.guild.id, "time":time, "announcement":message, "owner":ctx.author.id}
        DBupdate(ANNOUNCEMENTS_COL, {"server":ctx.guild.id, "owner":ctx.author.id}, announce)
        await reactOK(ctx)
        await self.before_timedannounce() # rebuild cache

    @commands.command()
    @commands.guild_only()
    async def removeannounce(self, ctx: commands.Context, time, *, message):
        '''
        Removes an announcement from the announcement system
        '''
        DBremove_one({"server":ctx.guild.id, "owner":ctx.author.id})
        await reactOK(ctx)
        await self.before_timedannounce()

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def testannounce(self, ctx: commands.Context, time):
        '''
        Tests making an announcement
        '''

        for a in self.announcements[ctx.guild.id]:

            if (time == a["time"]):
                c = await getChannel(ctx.guild, "announcements-channel")

                if hasattr(a["announcement"], "__call__"): await a["announcement"](c, ctx.guild.id) # daily announce
                    
                else: await c.send(a["announcement"])


