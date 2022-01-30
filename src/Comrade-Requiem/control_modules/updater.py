from dis_snek.models.snek import (Scale, slash_command,
                                  OptionTypes, slash_option,
                                  InteractionContext,
                                  is_owner)
from dis_snek.models.discord import Embed, MaterialColors
from logger import log
import os
import sys
from git import Repo


class Updater(Scale):
    @slash_command(name="reload",
                   sub_cmd_name="feature",
                   sub_cmd_description="reloads a feature module",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="feature", description="Feature module to reload",
                  opt_type=OptionTypes.STRING, required=True)
    async def reload_feature(self, ctx: InteractionContext, feature: str):
        ctx.bot.regrow_scale(f"feature_modules.{feature}")
        await ctx.send(f"Module successfully reloaded", ephemeral=True)

    @slash_command(name="reload",
                   sub_cmd_name="control",
                   sub_cmd_description="reloads a control module",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="control", description="Control module to reload",
                  opt_type=OptionTypes.STRING, required=True)
    async def reload_control(self, ctx: InteractionContext, control: str):
        ctx.bot.regrow_scale(f"control_modules.{control}")
        await ctx.send(f"Module successfully reloaded", ephemeral=True)
    
    @slash_command(name="update",
                   description="Updates the bot",
                   scopes=[419214713252216848, 709954286376976425])
    async def install_update(self, ctx: InteractionContext):
        await ctx.defer()
        # Initialize repo, going up two layers to get to the root
        repo = Repo(
            os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.abspath(
                            os.getcwd()))), ".git"))
        
        current_commit = repo.head.commit
        
        repo.remotes.origin.pull()
        
        latest_commit = repo.head.commit
        
        if current_commit.hexsha != latest_commit.hexsha:
            
            e = Embed(title="New update found and pulled.",
                      description="Reload/Restart for changes to take effect.",
                      color=MaterialColors.GREEN)
            e.set_thumbnail(url=ctx.bot.user.avatar.url)
            e.add_field(name=f"Current Commit ({current_commit.hexsha[:8]})",
                        value=f"Date: {current_commit.committed_datetime}")
            e.add_field(name=f"Latest Commit ({latest_commit.hexsha[:8]})",
                        value=f"Date: {latest_commit.committed_datetime}")
        else:
            e = Embed(title="No updates found.",
                      color=MaterialColors.GREY)
            e.set_thumbnail(url=ctx.bot.user.avatar.url)
            e.add_field(name=f"Latest Commit ({latest_commit.hexsha[:8]})",
                        value=f"Date: {latest_commit.committed_datetime}")
            
        await ctx.send(embed=e)

    @slash_command(name="restart",
                   description="Restarts the bot",
                   scopes=[419214713252216848, 709954286376976425])
    async def restart(self, ctx: InteractionContext):
        await ctx.send("Restarting...")
        await ctx.bot.stop()
        log.warn("Bot Restarting...")
        os.execl(sys.executable, sys.executable, sys.argv[0],
                 "--notify_channel", str(ctx.channel.id))


def setup(bot):
    Updater(bot)
    log.info("Module updater.py loaded.")
