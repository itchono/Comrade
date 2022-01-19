import dotenv
import os
from logger import logger

from dis_snek.client import Snake
from dis_snek.models.enums import Intents
from dis_snek.models.listener import listen
from dis_snek.models.application_commands import slash_command
from dis_snek.models.context import InteractionContext

dotenv.load_dotenv()  # Load .env file, prior to components loading


class CustomSnake(Snake):
    async def on_command_error(self, ctx: InteractionContext, error: Exception):
        logger.exception(msg = error, exc_info = error)
        if not ctx.responded:
            await ctx.send("Something went wrong.", ephemeral=True)

bot = CustomSnake(intents=Intents.ALL, sync_interactions=True)

@listen()
async def on_ready():
    print(f"{bot.user.username} is online.")


bot.grow_scale("modules.vault")
bot.grow_scale("modules.misc_fun")



bot.start(os.environ.get("TOKEN"))
