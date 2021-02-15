import time
import dotenv
import os

import components
from client import client as bot
from config import cfg
from utils.utilities import set_start_time, get_uptime
from utils.databases import rebuild_server_cfgs
from utils.users import rebuild_weight_table, sum_of_weights
from db import mongo_startup, RELAY_ID, relay_startup
from hosting.keep_alive import keep_alive
from utils.logger import logger


dotenv.load_dotenv()  # Load .env file, prior to components loading

# Startup operations
set_start_time(time.perf_counter())
mongo_startup()

for c in components.cogs:
    bot.add_cog(c(bot))


@bot.event
async def on_connect():
    '''
    Connected to Discord
    '''
    logger.info(
        f"{bot.user} is online, logged into {len(bot.guilds)} server(s).")


@bot.event
async def on_ready():
    '''
    Message cache etc. is ready
    '''
    rebuild_server_cfgs([guild for guild in bot.guilds if guild.id != RELAY_ID])
    await relay_startup(bot)

    logger.info("Server List:\n" +
                "\n".join(
                    f"\t{server.name} "
                    f"({len(server.members)} members)"
                    for server in bot.guilds))

    logger.info(f"Startup completed in {round(get_uptime(),3)}s")

    for guild in bot.guilds:
        if guild.id != int(
                cfg["Hosting"]["relay-id"]) and sum_of_weights(guild) == 0:
            await rebuild_weight_table(guild)

    if cfg["Settings"]["notify-on-startup"] == "True":
        owner = (await bot.application_info()).owner
        await owner.send("Bot is online.")

    # startup notify
    try:
        with open("restart.cfg", "r") as f:
            channel_id = int(f.read())
            channel = bot.get_channel(channel_id)
            await channel.send("Restart completed.")

        os.remove("restart.cfg")
        logger.info("Restart reminder found. Notifying channel.")
    except FileNotFoundError:
        pass

if cfg["Hosting"]["ping"] == "True":
    keep_alive()

bot.run(os.environ.get("TOKEN"))  # Run bot with loaded password
