from utils.utilities import *


import datetime

'''
Comrade - Time dependent modules
Timed announcements
'''

class TimeWizard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.announcements = {"08:00":self.dailyannounce}
        self._last_member = None

        self.timedannounce.start()

    def cog_unload(self):
        self.timedannounce.cancel()

    async def dailyannounce(self, channel: discord.TextChannel, serverDB: dict):
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

        d = DBuser(luckyperson.id, serverDB["_id"])
  
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
        await cog.userinfo(ctx, target=luckyperson.mention)
        
        await cog.rebuildcache(channel.guild)

    @tasks.loop(minutes=1.0)
    async def timedannounce(self):
        '''
        Makes an announcement
        '''
        servers = DBfind(SERVERCFG_COL)

        for s in servers:
            now = localTime()
            for a in self.announcements:
                if (now.strftime("%H:%M") == a):
                    c = self.bot.get_channel(s["announcements-channel"])
                    await self.announcements[a](c, s)
    

    @timedannounce.before_loop
    async def before_timedannounce(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def testannounce(self, ctx: commands.Context):
        '''
        Tests making an announcement
        '''
        await self.dailyannounce(ctx.channel, DBfind_one(SERVERCFG_COL, {"_id": ctx.guild.id}))


