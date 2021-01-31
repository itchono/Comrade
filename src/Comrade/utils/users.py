import discord
import random
import datetime
from client import client as bot
from db import collection
from config import cfg
from utils.utilities import ufil
from utils.logger import logger


def random_member_from_server(
        server_id: int, require_human=False) -> discord.Member:
    '''
    Returns a random member from a server
    '''
    server: discord.Guild = bot.get_guild(server_id)

    if require_human:
        members = [m for m in server.members if not m.bot]
    else:
        members = server.members

    return random.choice(members)


def weight_table(guild: discord.Guild) -> tuple:
    '''
    returns ids, weights of members in a server,
    for daily member roll.
    '''
    doc = collection("users").find({"server": guild.id})

    weights = [m["daily-weight"] for m in doc]
    doc.rewind()
    member_ids = [m["user"] for m in doc]

    return member_ids, weights


def sum_of_weights(guild: discord.Guild) -> int:
    '''
    Returns sum of weights in weight table
    '''
    _, weights = weight_table(guild)
    return sum(weights)


async def weighted_member_from_server(guild: discord.Guild) -> int:
    '''
    Yield the id of a random member from a guild,
    assuming the database is correctly defined
    '''
    if sum_of_weights(guild) > 0:
        return random.choices(*weight_table(guild))[0]
    return 0


async def rebuild_weight_table(guild: discord.Guild):
    '''
    Refills the daily member counts according to staleness rules.
    '''
    # Attempt to set default daily count
    server_cfg: dict = collection("servers").find_one(guild.id)

    if server_cfg["default-daily-count"] == 0:
        # Daily member turned off
        for member in guild.members:
            collection("users").update_one(
                ufil(member), {"$set": {"daily-weight": 0}})
        return

    logger.warning(
        f"{guild.name}: Cache is being reconstructed. This will take a while.")

    # Process staleness
    staleness = server_cfg["daily-member-staleness"]

    if staleness >= 0:
        threshold = datetime.datetime.now() - \
            datetime.timedelta(staleness)

        active_author_ids = set()

        for channel in guild.text_channels:

            active_ids_in_channel = await channel.history(
                limit=None, after=threshold).filter(
                    lambda msg: msg.type == discord.MessageType.default
            ).map(lambda msg: msg.author.id).flatten()

            active_author_ids.update(active_ids_in_channel)
    else:
        active_author_ids = set([member.id for member in guild.members])

    for member in guild.members:
        if (not member.bot or not bool(
            cfg["Settings"]["exclude-bots-from-daily"]))\
                and member.id in active_author_ids:
            daily = server_cfg["default-daily-count"]
        else:
            daily = 0

        collection("users").update_one(
            ufil(member), {"$set": {"daily-weight": daily}})

    logger.info(
        f"{guild.name}: Rebuilt weights for users in past {staleness} days")
