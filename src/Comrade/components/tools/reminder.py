import discord
from discord.ext import commands, tasks

import datetime

from utils.utilities import local_time
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
        if time[-1] == "d":
            advance = datetime.timedelta(days=float(time[:-1].strip()))
        elif time[-1] == "m":
            advance = datetime.timedelta(minutes=float(time[:-1].strip()))
        elif time[-1] == "h":
            advance = datetime.timedelta(hours=float(time[:-1].strip()))
        else:
            advance = datetime.timedelta(hours=float(time.strip()))

        reminder = {
            "server": ctx.guild is not None,
            "message": message,
            "time": datetime.datetime.utcnow() + advance,
            "user": ctx.author.id,
            "channel": ctx.channel.id if ctx.guild else 0,
            "jumpurl": ctx.message.jump_url
        }

        collection("reminders").insert_one(reminder)

        await ctx.send(
            f"I will remind you on <t:{(local_time() + advance).timestamp()}>.")

    @tasks.loop(minutes=1.0)
    async def send_reminders(self):
        reminders = collection(
            "reminders").find({"time": {"$lte": datetime.datetime.utcnow()}})

        for r in reminders:
            target = self.bot.get_user(r["user"])

            if r["server"]:
                channel = self.bot.get_channel(r["channel"])
            else:
                channel = target

            logger.info(f"Reminded {target}")

            embed = discord.Embed(color=0xd7342a, description=r["message"])
            embed.set_author(name=f"Reminder for {target.display_name}",
                             url=r["jumpurl"], icon_url=target.avatar_url)

            await channel.send(content=target.mention, embed=embed)

            collection("reminders").delete_one(r)

    @send_reminders.before_loop
    async def before_reminder(self):
        await self.bot.wait_until_ready()
