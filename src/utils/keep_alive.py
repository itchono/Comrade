from flask import Flask, render_template
from threading import Thread
from utils.utilities import *

import logging
import os

import requests
import json
import aiohttp
import urllib.request

logging.getLogger('werkzeug').disabled = True
os.environ['WERKZEUG_RUN_MAIN'] = 'true'

t_start = 0

app = Flask('')


@app.route('/')
def main():
    return 'Comrade is online - Uptime: {}'.format(localTime() -
                                                       t_start)


def run():
    global t_start
    t_start = localTime()
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()


def shutdown():
    server = Thread(target=run)
    server._stop()

# for repl.it
class SelfPing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lastping = None
        self.response = None
        self._last_member = None

        self.selfping.start()

    def cog_unload(self):
        self.selfping.cancel()

    @tasks.loop(minutes=1.0)
    async def selfping(self):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent}
        url = 'https://comrade--itchono.repl.co/'

        try:
            request = urllib.request.Request(url,None,headers)

            response = urllib.request.urlopen(request)
            self.response = response.read().decode("utf-8")
            self.lastping = localTime()
        except:
            print("ERROR pinging self!")

    @commands.command(name="ping")
    async def ping(self, ctx : commands.Context):
        await ctx.send("Last ping was at {}\nResponse:`{}`".format(self.lastping.strftime("%I:%M:%S %p %Z"), self.response))


    @selfping.before_loop
    async def before_selfping(self):
        await self.bot.wait_until_ready()
        print("Self ping routine started.")

