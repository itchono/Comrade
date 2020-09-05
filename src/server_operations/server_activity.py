import discord
from discord.ext import commands, tasks

import datetime

from utils import *

SERVER = 419214713252216848

class ActivityTracker(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

        self.online_humans = []
        self.messages_sent = 0
        self.quantities = {}

        self.datalog.start()

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

    
