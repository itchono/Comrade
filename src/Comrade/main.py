import dotenv
import os

from discord import HTTPException

from core.discord_client import client as bot

# Startup operations
dotenv.load_dotenv()  # Load .env file, prior to components loading
bot.load_extension("common")  # Load common infrastructure

try:
    bot.run(os.environ.get("TOKEN"))  # Run bot with loaded password
except HTTPException:
    os.system("kill 1")  # hard restart on 429
