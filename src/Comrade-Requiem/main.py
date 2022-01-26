import dotenv
import os
from logger import log

from dis_snek.client.const import __version__, __py_version__
from dis_snek.models.discord import Intents, Activity, ActivityType
from dis_snek.models.snek import listen

from custom_client import CustomSnake

dotenv.load_dotenv()  # Load .env file, prior to components loading

activity = Activity.create(name=" the rise of communism", type=ActivityType.WATCHING)

bot = CustomSnake(intents=Intents.new(
                        guild_members=True,
                        guild_messages=True,
                        direct_messages=True,
                        guild_emojis_and_stickers=True
                    ), sync_interactions=True,
                  delete_unused_application_cmds=True, activity=activity)
# TODO: May need to add "GUILDS" and "GUILD_EMOJIS_AND_STICKERS" to intents
# e.g. for emote system validation


@listen()
async def on_ready():
    log.info(f"{bot.user.username} is online, "
             f"running dis-snek version {__version__}"
             f" using Python {__py_version__}")


# Locate and load all modules under "control_modules"
for module in os.listdir("./control_modules"):
    if module.endswith(".py") and not module.startswith("_"):
        try:
            bot.grow_scale(f"control_modules.{module[:-3]}")
        except Exception as e:
            log.exception(f"Failed to load extension {module}")

# Locate and load all modules under "feature_modules"
for module in os.listdir("./feature_modules"):
    if module.endswith(".py") and not module.startswith("_"):
        try:
            bot.grow_scale(f"feature_modules.{module[:-3]}")
        except Exception as e:
            log.exception(f"Failed to load extension {module}")

bot.start(os.environ.get("DISCORD_BOT_TOKEN"))
