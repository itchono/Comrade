import dotenv
import os
from logger import logger

from dis_snek.client import Snake
from dis_snek.models.enums import Intents
from dis_snek.models.listener import listen
from dis_snek.models.context import InteractionContext

dotenv.load_dotenv()  # Load .env file, prior to components loading


class CustomSnake(Snake):
    async def on_command_error(self, ctx: InteractionContext,
                               error: Exception):
        logger.exception(msg=error, exc_info=error)
        if not ctx.responded:
            await ctx.send("Something went wrong.\n"
                           f"Error: `{error}`", ephemeral=True)


bot = CustomSnake(intents=Intents.ALL, sync_interactions=True,
                  delete_unused_application_cmds=True)


@listen()
async def on_ready():
    logger.info(f"{bot.user.username} is online.")


bot.grow_scale("modules.vault")
bot.grow_scale("modules.misc_fun")
bot.grow_scale("modules.website_searches")
bot.grow_scale("modules.text_modification")
bot.grow_scale("modules.image_modification")
bot.grow_scale("modules.telemetry")


bot.start(os.environ.get("TOKEN"))
