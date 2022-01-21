import dotenv
import os
from logger import log

from dis_snek.client import Snake
from dis_snek.models.enums import Intents
from dis_snek.models.listener import listen
from dis_snek.models.context import Context, InteractionContext, MessageContext
from dis_snek.models.discord_objects.activity import Activity, ActivityType

dotenv.load_dotenv()  # Load .env file, prior to components loading

class CustomSnake(Snake):
    async def on_command_error(self, ctx: Context,
                               error: Exception):
        log.exception(msg=error, exc_info=error)
        if type(ctx) == InteractionContext and not ctx.responded:
            await ctx.send("Something went wrong while executing the command.\n"
                           f"Error: `{error}`", ephemeral=True)
        elif type(ctx) == MessageContext:
            await ctx.send("Something went wrong while executing the command.\n"
                           f"Error: `{error}`", reply_to = ctx.message)


activity = Activity.create(name=" the rise of communism", type=ActivityType.WATCHING, url="comrade.itchono.repl.co")

bot = CustomSnake(intents=Intents.ALL, sync_interactions=True,
                  delete_unused_application_cmds=True, activity=activity)


@listen()
async def on_ready():
    log.info(f"{bot.user.username} is online.")
    
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



bot.start(os.environ.get("TOKEN"))
