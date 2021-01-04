import discord
import random
from functools import lru_cache
import datetime

from client import client as bot
from db import collection
from config import cfg
from utils.utilities import ufil


def random_member_from_server(
        server_id: int, require_human=False) -> discord.Member:
    '''
    Returns a random member from a server
    '''
    server: discord.Guild = bot.get_guild(server_id)

    if require_human:
        members = [m for m in server.members if not m.bot]
    members = server.members

    return random.choice(members)


@lru_cache()
def weight_table(guild_id) -> tuple:
    '''
    returns ids, weights of members in a server,
    for daily member roll.
    '''
    doc = collection("users").find({"server": guild_id})

    weights = [m["daily-weight"] for m in doc]
    doc.rewind()
    member_ids = [m["user"] for m in doc]

    return member_ids, weights


async def weighted_member_id_from_server(guild: discord.Guild):
    '''
    Yield the id of a random member from a guild,
    assuming the database is correctly defined
    '''
    return random.choices(*weight_table(guild.id))[0]


async def rebuild_weight_table(guild: discord.Guild):
    '''
    Update the daily weights in a given server
    Assumes user profiles are updated correctly.

    Operates in two modes:
    - If list is not empty: invalidates LRU cache
    - If list is empty: rebuilds all weights and resets cache
    '''
    _, weights = weight_table(guild.id)

    sum_of_weights = sum(weights)

    if sum_of_weights == 0:
        # Must reconstruct cache

        # Attempt to set default daily count
        server_cfg: dict = collection("servers").find_one(guild.id)

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

                active_author_ids += set(active_ids_in_channel)
        else:
            active_author_ids = set([member.id for member in guild.members])

        for member in guild.members:
            if not member.bot or not bool(
                    cfg["Settings"]["exclude-bots-from-daily"])\
                        or member.id not in active_author_ids:
                daily = server_cfg["default-daily-count"]
            else:
                daily = 0

            collection("users").update_one(
                ufil(member, guild), {"$set": {"daily-weight": daily}})

    weight_table.cache_clear()  # invalidate cache
