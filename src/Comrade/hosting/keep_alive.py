from discord.ext import commands, tasks
from flask import Flask
# used to create web server to keep bot actively hosted
from threading import Thread
# used to create separate parallel process to keep bot up

import urllib.request

from config import cfg
from utils.utilities import local_time, get_uptime, webscrape_header

# # disable logging
# import logging, os

# logging.getLogger('werkzeug').disabled = True
# os.environ['WERKZEUG_RUN_MAIN'] = 'true'

app = Flask('')


@app.route('/')
def main():
    return f"Bot is online. Uptime: {get_uptime()}"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_alive():
    server = Thread(target=run)
    server.start()


'''
This basically pings my other bots on repl.it and itself, to keep itself up
'''

with open("static/other_bots.txt", "r") as f:
    other_hosts = f.read().splitlines()


class Hosting(commands.Cog):
    '''
    Module to manage Comrade's remote hosting
    '''

    def __init__(self, bot):
        self.bot = bot
        self.lastping = None

        self.selfping.start()

    def cog_unload(self):
        self.selfping.cancel()

    @tasks.loop(seconds=30.0)
    async def selfping(self):
        me = cfg["Hosting"]["boturl"]

        for url in other_hosts + [me]:
            try:
                request = urllib.request.Request(url, None, webscrape_header())
                response = urllib.request.urlopen(request)

                if url == me:
                    self.lastping = {
                        "message": response.read().decode("utf-8"),
                        "time": local_time()}
            except Exception as ex:
                print(f"ERROR pinging {url}: {ex}")

    @commands.command()
    async def lastping(self, ctx: commands.Context):
        '''
        Shows when the bot last pinged itself
        '''
        await ctx.send(f"Last ping was at {self.lastping['time'].strftime('%I:%M:%S %p %Z')}\nResponse:`{self.lastping['message']}`")

    @commands.command()
    @commands.check_any(commands.is_owner())
    async def shutdown(self, ctx: commands.Context):
        '''
        Logs out the user.
        '''
        await self.bot.close()

    @selfping.before_loop
    async def before_selfping(self):
        await self.bot.wait_until_ready()
        print("Self ping routine started.")
