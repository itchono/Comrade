from dis_snek.models.snek import (InteractionContext, Scale,
                                  slash_command, OptionTypes, slash_option)
from processors.emote_system import ComradeEmoji
from logger import log


class EmoteManager(Scale):

    @slash_command(name="emote",
                   sub_cmd_name="use",
                   sub_cmd_description="Use an emote")
    @slash_option(name="emote", description="Emote to use",
                  opt_type=OptionTypes.STRING, required=True)
    async def emote_use(self, ctx: InteractionContext, emote: ComradeEmoji):
        await ctx.send(f"Emote located: {emote}")

def setup(bot):
    EmoteManager(bot)
    log.info("Module emote_manager.py loaded.")
