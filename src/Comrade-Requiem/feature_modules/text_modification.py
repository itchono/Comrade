from dis_snek.models.snek import (Scale, slash_command,
                                  OptionTypes, slash_option,
                                  InteractionContext)
from effectors.send_image_text import send_amongus
from logger import log
import textwrap


class TextModification(Scale):
    @slash_command(name="amongus",
                   description="Print out text in amongus font",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="text", description="Text to print",
                  opt_type=OptionTypes.STRING, required=True)
    async def amongus(self, ctx: InteractionContext, text: str):
        await send_amongus(ctx, text)
        
    @slash_command(name="news",
                   description="Wraps a piece of text in a fancy border for news",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="text", description="Text to print",
                  opt_type=OptionTypes.STRING, required=True)
    async def news(self, ctx: InteractionContext, text: str):
        with open("static/news_border.txt", "r", encoding="utf-8") as f:
            BORDER_TOP, ACCENT_BORDER, BORDER_BOTTOM = f.read().splitlines()
            len_border = len(BORDER_TOP)
            
        # Wrap and center the text according to the length of the border
        text = textwrap.wrap(text, width=len_border)
        text = "\n".join([line.center(len_border) for line in text])

        await ctx.send(f"**```{BORDER_TOP}\n{ACCENT_BORDER}\n{text}\n{ACCENT_BORDER}\n{BORDER_BOTTOM}```**")

def setup(bot):
    TextModification(bot)
    log.info("Module text_modification.py loaded.")
