
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
        await self.bot.wait_until_ready()

        servers = list(cfgQuery(None))

        for s in servers:
            ld = pytz.timezone("Canada/Eastern").localize(datetime.datetime.strptime(s["last daily"], "%Y-%m-%d"))
            now = pytz.timezone("Canada/Eastern").localize(datetime.datetime.now())

            if now.date() > ld.date() and now.hour >= 8:
                c = self.bot.get_channel(s["announcements channel"])
                m = await c.send("Good morning everyone! Today is {}. Have a great day.".format(now.strftime("%A, %B %d")))
                
                s["last daily"] = str(now.date())
                updateCFG(s)

                '''
                Daily user
                '''
                cog = self.bot.get_cog("Users")

                pool = []

                ctx = await self.bot.get_context(m)
                
                if (datetime.datetime.utcnow() - cog.RND_USER_T > datetime.timedelta(hours = 1)):
                    pool = cog.rebuildusercache(ctx)
                else:
                    pool = cog.RND_USER[:]

                random.shuffle(pool)
                luckyperson = pool.pop()

                await c.send("Today's Bonus Daily Member is {}".format(luckyperson.display_name))
                
                # up everyone's percentage

                for member in ctx.guild.members:
                    d = getUser(member.id, ctx.guild.id)
                    d["daily weight"] += 1 if member != luckyperson else 0
                    updateUser(d)

                await cog.userinfo(ctx, luckyperson.display_name)

                return
            else:
                return

    
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


