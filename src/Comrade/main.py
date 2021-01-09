import time
import dotenv
import discord
import os

import components
from client import client as bot
from config import cfg
from utils.utilities import set_start_time, get_uptime, dm_channel
from utils.databases import rebuild_server_cfgs
from utils.users import rebuild_weight_table, sum_of_weights
from db import gc_startup, mongo_startup
from hosting.keep_alive import keep_alive
from utils.logger import logger


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
    logger.info(
        f"{bot.user} is online, logged into {len(bot.guilds)} server(s).")
    online = True


@bot.event
async def on_ready():
    '''
    Message cache etc. is ready
    '''
    rebuild_server_cfgs(bot.guilds)

    logger.info("Server List:\n" +
                "\n".join(
                    f"\t{server.name} "
                    f"({len(server.members)} members)"
                    for server in bot.guilds))

    logger.info(f"Startup completed in {round(get_uptime(),3)}s")

    for guild in bot.guilds:
        if sum_of_weights(guild) == 0:
            await rebuild_weight_table(guild)

    if cfg["Settings"]["notify-on-startup"]:
        owner = (await bot.application_info()).owner
        owner_dm_channel = await dm_channel(owner)
        await owner_dm_channel.send("Bot is online.")

if bool(cfg["Hosting"]["ping"]):
    keep_alive()

bot.run(os.environ.get("TOKEN"))  # Run bot with loaded password
