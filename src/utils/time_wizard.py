
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
        self._last_member = None

        self.dailyannounce.start()

    
    @tasks.loop(minutes=5.0)
    async def dailyannounce(self):

        servers = list(cfgQuery(None))

        for s in servers:
            ld = datetime.strptime(s["last daily"], "%Y-%m-%d")

            if datetime.utcnow().date() > ld.date() and datetime.utcnow().hour == 12:
                g = self.bot.fetch_guild(s["_id"])

                await getChannel(g, "announcements chanel").send("Good morning everyone")
                s["last daily"] = str(datetime.utcnow().date())
                updateCFG(s)


