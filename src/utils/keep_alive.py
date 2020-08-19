from utils.utilities import *
from flask import Flask # used to create web server to keep bot actively hosted
from threading import Thread # used to create separate parallel process to keep bot up

import urllib.request

# disable logging
import logging
import os

logging.getLogger('werkzeug').disabled = True
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

app = Flask('')

start_time = localTime()

@app.route('/')
def main(): return f"Bot is online. Uptime: {localTime() - start_time}"

def run(): app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

### Self-sustain module

'''
This basically pings my other bots on repl.it and itself, to keep itself up
'''

class SelfPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lastping = None
        
        self.selfping.start()

    def cog_unload(self):
        self.selfping.cancel()

    @tasks.loop(seconds=30.0)
    async def selfping(self):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent}
        
        urls = ['https://Comrade.itchono.repl.co', 'https://DadBot.itchono.repl.co', 
        'https://SET-Bot.itchono.repl.co', 'https://psi-tama.itchono.repl.co'] # pinging my other bots

        me = 'https://Comrade.itchono.repl.co'

        for url in urls:
            try:
                request = urllib.request.Request(url,None,headers)
                response = urllib.request.urlopen(request)

                if url == me: self.lastping = {"message":response.read().decode("utf-8"), "time":localTime()}
            except: print(f"ERROR pinging {url}")

    @commands.command(aliases = ["stalk"])
    async def ping(self, ctx : commands.Context):
        '''
        Shows when the bot last pinged itself
        '''
        await ctx.send(f"Last ping was at {self.lastping['time'].strftime('%I:%M:%S %p %Z')}\nResponse:`{self.lastping['message']}`")

    @selfping.before_loop
    async def before_selfping(self):
        await self.bot.wait_until_ready()
        print("Self ping routine started.")