import discord
from discord.ext import commands, tasks

import datetime, pytz, io
from matplotlib import pyplot as plt
import matplotlib.dates as md
import numpy as np

from utils import *

SERVER = 419214713252216848

class ActivityTracker(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

        self.online_humans = []
        self.messages_sent = 0
        self.quantities = {}

        self.datalog.start()

        self.id2name = {}

    async def pushdata(self):
        '''
        Logs activity from all online members and pushes to remote
        '''
        server = self.bot.get_guild(SERVER)

        entry = {"time":localTime(), "online-members":len(self.online_humans), "messages-sent":self.messages_sent, "quantities":self.quantities}

        DBupdate("activitydata", {"time":localTime()}, entry)
        print("Data Logged.", entry)

        # PREPARE NEXT CYCLE
        self.online_humans = [m for m in server.members if (str(m.status) != "offline" and not m.bot)]
        self.messages_sent = 0
        self.quantities = {}
    
    @tasks.loop(minutes = 10)
    async def datalog(self):
        await self.pushdata()
        

    @datalog.before_loop
    async def before_log(self):
        await self.bot.wait_until_ready()

        server = self.bot.get_guild(SERVER)
        self.online_humans = [m for m in server.members if (str(m.status) != "offline" and not m.bot)]

        for m in server.members:
            self.id2name[m.id] = m.display_name

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        '''
        Listens from messages from invisible users
        '''
        if not message.author.bot: 
            self.messages_sent += 1

            try: self.quantities[str(message.author.id)] += 1
            except: self.quantities[str(message.author.id)] = 1

            if not message.author in self.online_humans: self.online_humans.append(message.author)

    @commands.command()
    @commands.guild_only()
    async def leaderboard(self, ctx):
        '''
        Pulls up the leaderboard for the server.
        '''
        await ctx.trigger_typing()

        entries = DBfind("activitydata", {})

        times = []
        bars = {}

        tz = pytz.timezone("US/Eastern")

        for t in entries:
            times.append(md.date2num(t["time"]))

            for person in t["quantities"]:
                try: bars[person] += t["quantities"][person]
                except: bars[person] = t["quantities"][person]
        fig = plt.figure()

        ax = fig.add_subplot(111)

        xs = np.arange(len(bars))

        sorted_keys = [e for _, e in sorted(zip(bars.values(), bars.keys()))]

        ax.set_title("Number of Messages by Person")
        ax.barh(xs, sorted(bars.values()))

        ax.set_yticks(np.arange(len(bars)))
        ax.set_yticklabels([self.id2name[int(i)] for i in sorted_keys])

        plt.subplots_adjust(left=0.4)

        f = io.BytesIO()
        plt.savefig(f, format="png")
        f.seek(0)
        plt.clf()
        await ctx.send(file=discord.File(f, "leaderboard.png"))

