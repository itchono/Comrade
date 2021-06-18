from discord.ext import commands
import os
from common.logger import logger
from common.utilities import get_uptime
from common.relay import startup


class Startup(commands.Cog):
    def __init__(self, bot: commands.bot) -> None:
        super().__init__

    @commands.Cog.listener()
    async def on_connect(self):
        '''
        Connected to Discord
        '''
        logger.info(
            f"{self.bot.user} is online, logged into {len(self.bot.guilds)} server(s).")


    @commands.Cog.listener()
    async def on_ready(self):
        '''
        Message cache etc. is ready
        '''
        await startup(self.bot)
        rebuild_server_cfgs([guild for guild in bot.guilds if guild.id != RELAY_ID])

        logger.info("Server List:\n" +
                    "\n".join(
                        f"\t{server.name} "
                        f"({len(server.members)} members)"
                        for server in bot.guilds))

        logger.info(f"Startup completed in {round(get_uptime(),3)}s")

        for guild in self.bot.guilds:
            if guild.id != int(
                    cfg["Hosting"]["relay-id"]) and sum_of_weights(guild) == 0:
                await rebuild_weight_table(guild)

        if cfg["Settings"]["notify-on-startup"] == "True":
            owner = (await bot.application_info()).owner
            await owner.send("Bot is online.")

        # startup notify
        try:
            with open("restart.cfg", "r") as f:
                channel_id = int(f.read())
                if channel := bot.get_channel(channel_id):
                    await channel.send(f"Restart completed. Version is: {version}")
                elif user := bot.get_user(channel_id):
                    await user.send(f"Restart completed. Version is: {version}")

            os.remove("restart.cfg")
            logger.info("Restart reminder found. Notifying channel.")
        except FileNotFoundError:
            pass