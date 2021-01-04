import time
import dotenv
import discord
import os

import components
from client import client as bot
from config import cfg
from utils.utilities import set_start_time, get_uptime, local_time
from utils.databases import rebuild_server_cfgs
from db import gc_startup, mongo_startup
from hosting.keep_alive import keep_alive

dotenv.load_dotenv()  # Load .env file, prior to components loading

# Startup operations
set_start_time(time.perf_counter())
gc_startup()
mongo_startup()

for c in components.cogs:
    bot.add_cog(c(bot))

online = False


@bot.event
async def on_connect():
    '''
    Connected to Discord
    '''
    global online
    await bot.change_presence(status=discord.Status.online,
                              activity=discord.Game(cfg["Settings"]["Status"]))
    print(f"{bot.user} is logged into {len(bot.guilds)} server(s).")
    online = True


@bot.event
async def on_ready():
    '''
    Message cache etc. is ready
    '''
    rebuild_server_cfgs(bot.guilds)

    print("Server List:"
          "\n".join(
              f"\t{server.name} "
              f"({len(server.members)} members)"
              for server in bot.guilds) +
          f"\nStartup completed in {round(get_uptime(),3)}s ("
          f"{local_time().strftime('%I:%M:%S %p %Z')})")

if bool(cfg["Hosting"]["ping"]):
    keep_alive()

bot.run(os.environ.get("TOKEN"))  # Run bot with loaded password
