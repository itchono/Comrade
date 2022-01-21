from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import (slash_command,
                                                  OptionTypes, slash_option)
from dis_snek.models.context import InteractionContext
from logger import log


class Updater(Scale):
    @slash_command(name="reload_feature",
                   description="reloads a feature module",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="feature", description="Feature module to reload",
                  opt_type=OptionTypes.STRING, required=True)
    async def amongus(self, ctx: InteractionContext, feature: str):
        await ctx.bot.regrow_scale(f"feature_modules.{feature}")
        await ctx.send(f"Module successfully reloaded", ephemeral=True)

def setup(bot):
    Updater(bot)
    log.info("Module updater.py loaded.")
