from dis_snek.models.snek import (Scale, slash_command,
                                  OptionTypes, slash_option,
                                  InteractionContext)
from logger import log
import os
import sys
import aiohttp
from git import Repo


class Updater(Scale):
    @slash_command(name="reload_feature",
                   description="reloads a feature module",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="feature", description="Feature module to reload",
                  opt_type=OptionTypes.STRING, required=True)
    async def reload_feature(self, ctx: InteractionContext, feature: str):
        await ctx.bot.regrow_scale(f"feature_modules.{feature}")
        await ctx.send(f"Module successfully reloaded", ephemeral=True)
        
    @slash_command(name="install_update",
                   description="Updates the bot",
                   scopes=[419214713252216848, 709954286376976425])
    async def install_update(self, ctx: InteractionContext):
        await ctx.defer()
        # Initialize repo, going up two layers to get to the root
        repo = Repo(
            os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(__file__))), ".git"))
        
        current_commit = repo.head.commit
        
        repo.remotes.origin.pull()
        
        current_commit = repo.head.commit
        
        if current_commit.hexsha != repo.head.commit.hexsha:
            await ctx.send(f"New update found and pulled. Restart for changes to take effect.")
        else:
            await ctx.send(f"No new updates found.")
        
    @slash_command(name="restart",
                   description="Restarts the bot",
                   scopes=[419214713252216848, 709954286376976425])
    async def restart(self, ctx: InteractionContext):
        await ctx.send("Restarting...", ephemeral=True)
        await ctx.bot.stop()
        log.warn("Bot Restarting...")
        os.execl(sys.executable, sys.executable, *sys.argv)


def setup(bot):
    Updater(bot)
    log.info("Module updater.py loaded.")
