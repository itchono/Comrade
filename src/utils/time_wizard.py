
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
                await c.send("Good morning everyone! Today is {}. Have a great day.".format(now.strftime("%A, %B %d")))
                s["last daily"] = str(now.date())
                updateCFG(s)
    
    @dailyannounce.before_loop
    async def before_dailyannounce(self):
        print('waiting for login to check announcements...')
        await self.bot.wait_until_ready()

    @commands.command()
    async def testannounce(self, ctx: commands.Context):
        '''
        Tests making an announcement
        '''
        self.dailyannounce.cancel()
        self.dailyannounce.start()


