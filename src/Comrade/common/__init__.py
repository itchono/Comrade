# Common infrastructure of Comrade used to support other modules
# Reloading can be done in the same way as discord.py extensions
# Discord.py reload will also re-import the modules

import os
from .logger import logger
from discord.ext import commands


def setup(bot):
    # Entry point for extension
    _, _, files = next(os.walk("./common"))
    # Load all .py files
    for name in files:
        if len(name) > 3 and name[-3:] == ".py" and not name == "__init__.py":
            try:
                bot.load_extension(f"common.{name[:-3]}")
            except commands.ExtensionFailed as e:
                logger.info(f"Failure to load: {name[:-3]}\n{e}")
            else:
                logger.info(f"Loaded infrastructure: {name[:-3]}")
