from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import (slash_command,
                                                  OptionTypes, slash_option)
from dis_snek.models.context import InteractionContext
from logger import logger


class TextModification(Scale):
    pass

def setup(bot):
    TextModification(bot)
    logger.info("Module text_modification.py loaded.")
