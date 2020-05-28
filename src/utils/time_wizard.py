from utils.utilities import *
from utils.mongo_interface import *

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

        m = await channel.send("Good morning everyone! Today is {}. Have a great day.".format(now.strftime("%A, %B %d. It's %I:%M:%S %p")))
        
        serverDB["last daily"] = str(now.date())
        updateCFG(serverDB)

        '''
        Daily user
        '''
        cog = self.bot.get_cog("Users")

        ctx = await self.bot.get_context(m)
        
        pool = cog.RND_USER[serverDB["_id"]][:]

        random.shuffle(pool)
        luckyperson = pool.pop()

        d = getUser(luckyperson.id, serverDB["_id"])
        d["daily weight"] -= 1
        updateUser(d)
        # self regulating; once probability drops to zero, we just need to refill.

        await channel.send("Today's Bonus Daily Member is {}".format(luckyperson.display_name))
        await cog.userinfo(ctx, target=luckyperson.mention)

        dailyrole = await dailyRole(channel.guild)

        for m in dailyrole.members:
            # remove bearer of previous daily role
            roles = m.roles
            roles.remove(dailyrole)
            await m.edit(roles=roles)
        
        roles = luckyperson.roles
        roles.append(dailyrole)
        await luckyperson.edit(roles=roles)
        
        await cog.rebuildUserCache()

    @tasks.loop(minutes=1.0)
    async def timedannounce(self):
        '''
        Makes an announcement
        '''
        servers = list(cfgQuery(None))

        for s in servers:
            now = localTime()
            for a in self.announcements:
                if (now.strftime("%H:%M") == a):
                    c = self.bot.get_channel(s["announcements channel"])
                    await self.announcements[a](c, s)
    

    @timedannounce.before_loop
    async def before_timedannounce(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.check(isOwner)
    async def testannounce(self, ctx: commands.Context):
        '''
        Tests making an announcement
        '''
        await self.dailyannounce(ctx.channel, getCFG(ctx.guild.id))


