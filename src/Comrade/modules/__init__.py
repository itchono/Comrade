# Modules interface for Comrade
# Features autoloading for all extensions placed into this folder

import os
from common.logger import logger


def setup(bot):
    # Entry point for extension
    _, _, files = next(os.walk("./modules"))
    # Load all .py files
    for name in files:
        if len(name) > 3 and name[-3:] == ".py" and not name == "__init__.py":
            logger.info(f"Loading module: {name[:-3]}")
            bot.load_extension(f"modules.{name[:-3]}")
