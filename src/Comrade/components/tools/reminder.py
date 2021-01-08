from discord.ext import commands, tasks

import datetime

from utils.utilities import local_time, dm_channel
from db import collection

from utils.logger import logger


class Reminders(commands.Cog):
    '''
    Remind you in the future
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.send_reminders.start()

    def cog_unload(self):
        self.send_reminders.cancel()

    @commands.command()
    async def remind(self, ctx: commands.context, time: str, *, message: str):
        '''
        Adds a reminder in some amount of time.
        Time should be specified as "1d" "60m" "23h" etc.
        Supports minutes, hours, days.
        Defaults to hours if no unit given.
        '''
        now = local_time()
        logger.info(now)


        if time[-1] == "d":
            advance = datetime.timedelta(days=float(time[:-1].strip()))
        elif time[-1] == "m":
            advance = datetime.timedelta(minutes=float(time[:-1].strip()))
        else:
            advance = datetime.timedelta(hours=float(time[:-1].strip()))

        remind_time = now + advance
        logger.info(remind_time)

        reminder = {
            "server": ctx.guild is not None,
            "message": message,
            "time": remind_time,
            "user": ctx.author.id,
            "channel": ctx.channel.id if ctx.guild else 0
        }

        collection("reminders").insert_one(reminder)

        await ctx.send(
            f"I will remind you at {remind_time.strftime('%B %m %Y at %I:%M %p %Z')}.")

    @tasks.loop(minutes=1.0)
    async def send_reminders(self):
        reminders = collection(
            "reminders").find({"time": {"$lte": local_time()}})

        for r in reminders:
            target = self.bot.get_user(r["user"])

            if r["server"]:
                channel = self.bot.get_channel(r["channel"])
            else:
                channel = dm_channel(target)

            await channel.send(f"{target.mention}: {r['message']}")

            collection("reminders").delete_one(r)
