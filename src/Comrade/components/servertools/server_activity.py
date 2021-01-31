'''
Experimental file

Used to log activity data of server users over a period of about 4 months.

Code maintained here only as reference.
'''


# from typing import Collection
# import discord
# from discord.ext import commands, tasks

# import pytz
# import io
# from matplotlib import pyplot as plt
# from scipy.interpolate import interp1d
# import matplotlib.dates as md
# import numpy as np

# from utils.utilities import local_time
# from db import collection

# SERVER = 419214713252216848


# def interpdays(times, values):
#     '''
#     Returns an averaged graph of all the days
#     '''
#     fc = interp1d(times, values)

#     DAY_MIN = int(times[0])
#     DAY_MAX = int(times[-1])

#     if DAY_MIN == DAY_MAX:
#         return (times, values)  # can't do anything with this
#     else:
#         sampletimes = np.linspace(
#             times[0], times[0] + 1, 100)  # 24 hour period
#         onlines = []

#         for time in sampletimes:
#             s = 0
#             avgcount = 0
#             for day in range(DAY_MAX - DAY_MIN):
#                 try:
#                     s += fc(time + day)
#                     avgcount += 1
#                 except BaseException:
#                     pass  # if the date doesn't exist in the domain

#             onlines.append(s / avgcount)
#         return (sampletimes, np.array(onlines))


# class ActivityTracker(commands.Cog):
#     def __init__(self, bot):
#         self.bot: commands.Bot = bot

#         self.online_humans = []
#         self.messages_sent = 0
#         self.quantities = {}

#         self.datalog.start()

#         self.id2name = {}

#     async def pushdata(self):
#         '''
#         Logs activity from all online members and pushes to remote
#         '''
#         server = self.bot.get_guild(SERVER)

#         entry = {"time": local_time(),
#                  "online-members": len(self.online_humans),
#                  "messages-sent": self.messages_sent,
#                  "quantities": self.quantities}
#         collection("activitydata").insert_one(entry)
#         # print("Data Logged.", entry)

#         # PREPARE NEXT CYCLE
#         self.online_humans = [m for m in server.members if (
#             str(m.status) != "offline" and not m.bot)]
#         self.messages_sent = 0
#         self.quantities = {}

#     @tasks.loop(minutes=10)
#     async def datalog(self):
#         await self.pushdata()

#         # also rebuild user cache
#         server = self.bot.get_guild(SERVER)
#         for m in server.members:
#             self.id2name[m.id] = m.display_name

#     @datalog.before_loop
#     async def before_log(self):
#         await self.bot.wait_until_ready()

#         server = self.bot.get_guild(SERVER)
#         self.online_humans = [m for m in server.members if (
#             str(m.status) != "offline" and not m.bot)]
#         for m in server.members:
#             self.id2name[m.id] = m.display_name

#     @commands.Cog.listener()
#     async def on_message(self, message: discord.message):
#         '''
#         Listens from messages from invisible users
#         '''
#         if not message.author.bot:
#             self.messages_sent += 1

#             try:
#                 self.quantities[str(message.author.id)] += 1
#             except BaseException:
#                 self.quantities[str(message.author.id)] = 1

#             if message.author not in self.online_humans:
#                 self.online_humans.append(message.author)

#     @commands.command()
#     @commands.guild_only()
#     async def leaderboard(self, ctx, limit: int = 10):
#         '''
#         Pulls up the leaderboard for the server.
#         '''
#         await ctx.trigger_typing()

#         entries = collection("activitydata").find()

#         times = []
#         bars = {}

#         tz = pytz.timezone("US/Eastern")

#         for t in entries:
#             times.append(md.date2num(t["time"]))

#             for person in t["quantities"]:
#                 try:
#                     bars[person] += t["quantities"][person]
#                 except BaseException:
#                     bars[person] = t["quantities"][person]
#         fig = plt.figure()

#         ax = fig.add_subplot(111)

#         limit = len(bars) if limit > len(bars) else limit

#         xs = np.arange(limit)

#         sorted_keys = [e for _, e in sorted(zip(bars.values(), bars.keys()))]

#         ax.set_title(f"Number of Messages by Person (Top {limit})")

#         ax.barh(xs, sorted(list(bars.values()))[-limit:])

#         ax.set_yticks(np.arange(limit))
#         ax.set_yticklabels([self.id2name[int(i)] if int(
#             i) in self.id2name else i for i in sorted_keys][-limit:])

#         ax.set_xticks([])

#         plt.subplots_adjust(left=0.4)

#         f = io.BytesIO()
#         plt.savefig(f, format="png")
#         f.seek(0)
#         plt.clf()
#         await ctx.send(file=discord.File(f, "leaderboard.png"))

#     @commands.group(invoke_without_command=True)
#     @commands.guild_only()
#     async def onlinegraph(self, ctx):
#         '''
#         Displays a graph of the average number of people online at a given time over a single day
#         '''
#         await ctx.trigger_typing()

#         entries = collection("activitydata").find()

#         times = []
#         onlinepeople = []

#         tz = pytz.timezone("US/Eastern")

#         for t in entries:
#             times.append(md.date2num(t["time"]))
#             onlinepeople.append(t["online-members"])

#         times, onlinepeople = interpdays(times, onlinepeople)

#         fig = plt.figure()

#         ax = fig.add_subplot(111)

#         ax.set_title("Avg. Number of Online Members on Iraq BTW")
#         ax.plot_date(times, onlinepeople, "-")

#         ax.set_ylabel("Number of Members (Human, Online)")
#         ax.set_xlabel("Time")

#         xfmt = md.DateFormatter('%H:%M', tz=tz)
#         ax.xaxis.set_major_formatter(xfmt)

#         ax.grid()

#         f = io.BytesIO()
#         plt.savefig(f, format="png")
#         f.seek(0)
#         plt.clf()
#         await ctx.send(file=discord.File(f, "online.png"))

#     @onlinegraph.command(name="all")
#     @commands.guild_only()
#     async def allonline(self, ctx: commands.Context):
#         '''
#         Displays a graph of all logged online times
#         '''
#         await ctx.trigger_typing()

#         entries = collection("activitydata").find()

#         times = []
#         onlinepeople = []

#         tz = pytz.timezone("US/Eastern")

#         for t in entries:
#             times.append(md.date2num(t["time"]))
#             onlinepeople.append(t["online-members"])

#         fig = plt.figure()

#         ax = fig.add_subplot(111)

#         ax.set_title("Number of Online Members on Iraq BTW")
#         ax.plot_date(times, onlinepeople, "-")

#         ax.set_ylabel("Number of Members (Human, Online)")
#         ax.set_xlabel("Time")

#         xfmt = md.DateFormatter('%H:%M', tz=tz)
#         ax.xaxis.set_major_formatter(xfmt)

#         ax.grid()

#         f = io.BytesIO()
#         plt.savefig(f, format="png")
#         f.seek(0)
#         plt.clf()
#         await ctx.send(file=discord.File(f, "online.png"))

#     @commands.group(invoke_without_command=True)
#     @commands.guild_only()
#     async def messagegraph(self, ctx):

#         await ctx.trigger_typing()

#         entries = collection("activitydata").find()

#         times = []
#         messagevolume = []

#         tz = pytz.timezone("US/Eastern")

#         for t in entries:
#             times.append(md.date2num(t["time"]))
#             messagevolume.append(t["messages-sent"])

#         fig = plt.figure()

#         times, messagevolume = interpdays(times, messagevolume)

#         ax = fig.add_subplot(111)

#         ax.set_title("Message Volume")
#         ax.plot_date(times, messagevolume, "-")

#         ax.set_ylabel("Avg. Number of Messages Sent in Time Window")
#         ax.set_xlabel("Time")

#         xfmt = md.DateFormatter('%H:%M', tz=tz)
#         ax.xaxis.set_major_formatter(xfmt)

#         ax.grid()

#         f = io.BytesIO()
#         plt.savefig(f, format="png")
#         f.seek(0)
#         plt.clf()
#         await ctx.send(file=discord.File(f, "messages.png"))

#     @messagegraph.command(name="all")
#     @commands.guild_only()
#     async def allmessage(self, ctx: commands.Context):
#         await ctx.trigger_typing()

#         entries = collection("activitydata").find()

#         times = []
#         messagevolume = []

#         tz = pytz.timezone("US/Eastern")

#         for t in entries:
#             times.append(md.date2num(t["time"]))
#             messagevolume.append(t["messages-sent"])

#         fig = plt.figure()

#         ax = fig.add_subplot(111)

#         ax.set_title("Message Volume")
#         ax.plot_date(times, messagevolume, "-")

#         ax.set_ylabel("Number of Messages Sent in Time Window")
#         ax.set_xlabel("Time")

#         xfmt = md.DateFormatter('%H:%M', tz=tz)
#         ax.xaxis.set_major_formatter(xfmt)

#         ax.grid()

#         f = io.BytesIO()
#         plt.savefig(f, format="png")
#         f.seek(0)
#         plt.clf()
#         await ctx.send(file=discord.File(f, "messages.png"))
