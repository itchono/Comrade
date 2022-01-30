import os
from dis_snek.models.snek import Scale, listen
from dis_snek.models.discord import ChannelTypes
from logger import log


class Relay(Scale):
    @listen
    async def on_ready(self):
        RELAY_ID = int(os.environ.get("RELAY_SERVER_ID"))

        # Set up relay guild
        self.bot.relay_guild = \
            await self.bot.get_guild(RELAY_ID)

        if self.bot.relay_guild:
            log.info(f"Relay guild connected: {self.bot.relay_guild.name}")
        else:
            log.critical(
                f"Relay guild not found! Attempted connection ID: {os.environ.get('RELAY_SERVER_ID')}")
        
        # Set up relay channel
        self.bot.relay_channel = \
            next(filter(lambda x: x.name == "relay",
                        self.bot.relay_guild.channels), None)
            
        if not self.bot.relay_channel:
            self.bot.relay_channel = \
                await self.bot.relay_guild.create_text_channel(
                    channel_type=ChannelTypes.GUILD_TEXT,
                    name="relay")
            log.warn("Setting up relay channel (First time setup)")
            
        # Set up emote channels
        for guild in self.bot.guilds:
            if guild.id == RELAY_ID:
                continue
            
            self.bot.emote_channels[guild.id] = \
                next(filter(lambda x: x.name == f"emotes{guild.id}",
                            self.bot.relay_guild.channels), None)
                
            if not self.bot.emote_channels[guild.id]:
                self.bot.emote_channels[guild.id] = \
                    await self.bot.relay_guild.create_text_channel(
                        channel_type=ChannelTypes.GUILD_TEXT,
                        name=f"emotes{guild.id}")
        log.info("Relay setup completed!")


def setup(bot):
    Relay(bot)
    log.info("Module relay.py loaded.")


