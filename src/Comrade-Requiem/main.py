import dotenv
import os
import argparse
from logger import log

from dis_snek.client.const import __version__, __py_version__
from dis_snek.models.discord import Intents, Activity, ActivityType
from dis_snek.models.snek import listen

from custom_client import CustomSnake

dotenv.load_dotenv()  # Load .env file, prior to components loading

# Command line arguments
parser = argparse.ArgumentParser(description="Comrade Requiem")
parser.add_argument("--notify_channel", type=int,
                    help="Send a message to this channel after startup")
args = parser.parse_args()

activity = Activity.create(name=" the rise of communism", type=ActivityType.WATCHING)

bot = CustomSnake(intents=Intents.new(
                        guild_members=True,
                        guild_messages=True,
                        direct_messages=True,
                        guild_emojis_and_stickers=True
                    ), sync_interactions=True,
                  activity=activity,
                  enable_emoji_cache=True)


@listen()
async def on_ready():
    log.info(f"{bot.user.username} is online, "
             f"running dis-snek version {__version__}"
             f" using Python {__py_version__}")
    if args.notify_channel:
        channel = await bot.get_channel(args.notify_channel)
        await channel.send(f"{bot.user.display_name} is online.")


# Locate and load all modules under "control_modules"
for module in os.listdir("./control_modules"):
    if module.endswith(".py") and not module.startswith("_"):
        try:
            bot.grow_scale(f"control_modules.{module[:-3]}")
        except Exception:
            log.exception(f"Failed to load extension {module}")

# Locate and load all modules under "feature_modules"
for module in os.listdir("./feature_modules"):
    if module.endswith(".py") and not module.startswith("_"):
        try:
            bot.grow_scale(f"feature_modules.{module[:-3]}")
        except Exception:
            log.exception(f"Failed to load extension {module}")

bot.start(os.environ.get("DISCORD_BOT_TOKEN"))
