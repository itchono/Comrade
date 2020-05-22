
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
        self.message_buffer = []
        self._last_member = None

        self.dailyannounce.start()

    def cog_unload(self):
        self.dailyannounce.cancel()

    @tasks.loop(minutes=5.0)
    async def dailyannounce(self):
        '''
        Daily announcement, made at 8 AM Eastern Time
        TODO: Custom timezones
        '''
        servers = list(cfgQuery(None))

        for s in servers:
            ld = datetime.datetime.strptime(s["last daily"], "%Y-%m-%d")
            now = localTime()

            if now.date() > ld.date() and now.hour >= 8:
                c = self.bot.get_channel(s["announcements channel"])
                m = await c.send("Good morning everyone! Today is {}. Have a great day.".format(now.strftime("%A, %B %d. It's %I:%M:%S %p")))
                
                s["last daily"] = str(now.date())
                updateCFG(s)

                '''
                Daily user
                '''
                cog = self.bot.get_cog("Users")

                ctx = await self.bot.get_context(m)
                
                pool = cog.RND_USER[s["_id"]][:]

                random.shuffle(pool)
                luckyperson = pool.pop()

                d = getUser(luckyperson.id, s["_id"])
                d["daily weight"] -= 1
                updateUser(d)
                # self regulating; once probability drops to zero, we just need to refill.

                await c.send("Today's Bonus Daily Member is {}".format(luckyperson.display_name))
                await cog.userinfo(ctx, target=luckyperson.mention)
                
                cog.rebuildUserCache()
    
    @dailyannounce.before_loop
    async def before_dailyannounce(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def testannounce(self, ctx: commands.Context):
        '''
        Tests making an announcement
        '''
        self.dailyannounce.cancel()
        self.dailyannounce.start()


