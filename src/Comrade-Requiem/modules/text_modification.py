from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import (slash_command,
                                                  OptionTypes, slash_option)
from dis_snek.models.context import InteractionContext
from effectors.send_image_text import send_amongus
from logger import logger


class TextModification(Scale):
    @slash_command(name="amongus",
                   description="Print out text in amongus font",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="text", description="Text to print",
                  opt_type=OptionTypes.STRING, required=True)
    async def amongus(self, ctx: InteractionContext, text: str):
        await send_amongus(ctx, text)

def setup(bot):
    TextModification(bot)
    logger.info("Module text_modification.py loaded.")
