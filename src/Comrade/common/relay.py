import discord
from discord.ext import commands
from common.config import cfg
from common.logger import logger

# Relay server connection for Comrade

GO_ID = int(cfg["Hosting"]["go-id"])
RELAY_ID = int(cfg["Hosting"]["relay-id"])

relay_guild = None
relay_channel = None


def get_relay_channel():
    return relay_channel


def get_relay_guild():
    return relay_guild


async def startup(bot: commands.Bot):
    '''
    Runs during startup to set up the databases
    Wait until bot is ready, and then load relay stuff
    '''
    await bot.wait_until_ready()
    global relay_channel, relay_guild

    relay_guild = bot.get_guild(RELAY_ID)

    if relay_guild:
        logger.info(f"Relay connected to server: {relay_guild.name}")
    else:
        logger.error(f"Relay not connected! Attempted connection id: {RELAY_ID}")

    if not (channel := discord.common.get(
            relay_guild.text_channels, name="relay")):
        relay_channel = await relay_guild.create_text_channel("relay")
        logger.warn("Setting up server for relay (first time init)")
    else:
        relay_channel = channel

    for g in bot.guilds:
        if g.id != RELAY_ID and not (
                channel := emote_channel(g)):

            await relay_guild.create_text_channel(f"emotes{g.id}")

            logger.warn(f"Creating new emotes directory for server {g.id}")


def emote_channel(guild) -> discord.TextChannel:
    '''
    Returns emote channel of a guild, if it exists
    '''
    return discord.common.get(
        relay_guild.text_channels, name=f"emotes{guild.id}")


def setup(bot: commands.Bot):
    # Entry point for extension
    pass
