'''
Utilities related to databases
'''

import discord

from db import collection
from config import cfg
from utils.logger import logger


def new_server(guild: discord.Guild):
    '''
    Configures a new server for use, returns a dictionary ready to be updated
    '''
    # Attempt to locate channels automatically
    vault = discord.utils.find(
        lambda c: "vault" in c.name, guild.text_channels)
    announcements = discord.utils.find(
        lambda c: "announcements" in c.name, guild.text_channels)

    return {
        "_id": guild.id,
        "jokes": True,
        # allows for joke stuff to happen

        "thresholds":
            {
                "kick": 6,
                "mute": 4,
                "zahando": 3
            },

        "global-banned-words": {},

        "default-daily-count": 0,
        # amount of daily member counts everyone starts with
        # Set to 0 by default.

        "daily-member-staleness": 15,
        # only users active in the last n days are considered
        # for daily membership. Set to -1 (or less) to include all members.

        "channels":
            {
                "vault": vault.id if vault else 0,
                "announcements": announcements.id if announcements else 0,
                "custom": 0
        },

        "durations":
            {
                "zahando": 120,
                # time to vote for ZA HANDO, in seconds
                "vault": 180
                # time to vote for Vault post, in seconds
        }

    }


def new_user(user: discord.Member):
    '''
    Configures a new user for use, returns a dictionary ready to be updated
    '''

    # Attempt to set default daily count
    server_cfg: dict = collection("servers").find_one(user.guild.id)

    if not user.bot or cfg["Settings"]["exclude-bots-from-daily"] == "False":
        daily = server_cfg["default-daily-count"]
    else:
        daily = 0

    return {
        "user": user.id,
        "server": user.guild.id,
        "last-online": "Now" if str(user.status) == "online" else "Never",
        "OP": False,
        "daily-weight": daily,
        "notify-status": [],

        "identity": "",

        "guessing-game":
            {
                "highest-streak": 0
        },

        "moderation":
            {
                "stop-pings": False,
                "stop-images": False,
                "banned-words": {},
                "kick-votes": [],
                "mute-votes": [],
                "threat-level": 0
        },
    }


def rebuild_server_cfgs(guilds: list):
    '''
    Rebuilds server configuration
    '''
    logger.info("Scanning for new servers...")

    DB_guilds = collection("servers").find()

    guild_ids = [g["_id"] for g in DB_guilds]

    actual_guild_ids = [g.id for g in guilds]

    for guild in guilds:
        if guild.id not in guild_ids:
            logger.info(f"New Server Found: {guild.name}")
            collection("servers").insert_one(new_server(guild))
        rebuild_user_profiles(guild)  # check users too

    for g_id in guild_ids:
        if g_id not in actual_guild_ids and \
                cfg["Settings"]["development-mode"] == "False":
            logger.info("Deleting Old Server & Members")
            collection("servers").delete_one({"_id": g_id})
            collection("users").delete_many({"server": g_id})

    logger.info("Server scan DONE")


def rebuild_user_profiles(guild: discord.Guild):
    '''
    Rebuilds user profiles within a given server
    '''
    logger.info(f"{guild.name}: Scanning for new members...")

    DB_members = collection("users").find({"server": guild.id})

    member_ids = [m["user"] for m in DB_members]

    actual_member_ids = [m.id for m in guild.members]

    # Scan to add new
    for member in guild.members:
        if member.id not in member_ids:
            logger.info(f"New Member Found in {guild.name}")
            collection("users").insert_one(new_user(member))

    # Scan to remove old
    for mem_id in member_ids:
        if mem_id not in actual_member_ids:
            logger.info(f"Deleting Old Member Found in {guild.name}")
            collection("users").delete_one(
                {"server": guild.id, "user": mem_id})
