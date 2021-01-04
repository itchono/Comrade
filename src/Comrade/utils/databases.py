'''
Utilities related to databases
'''

import discord

from db import collection
from config import cfg
from utils.utilities import ufil


def new_server(guild: discord.Guild):
    '''
    Configures a new server for use, returns a dictionary ready to be updated
    '''
    # Attempt to locate channels automatically
    log = discord.utils.find(
        lambda c: "log" in c.name, guild.text_channels)
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

        "default-daily-count": 2,
        # amount of daily member counts everyone starts with

        "daily-member-staleness": 15,
        # only users active in the last n days are considered
        # for daily membership. Set to -1 (or less) to include all members.

        "channels":
            {
                "vault": 0,
                "announcements": announcements.id if announcements else 0,
                "log": log.id if log else 0,
                "custom": 0,

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

    if not user.bot or not bool(
            cfg["Settings"]["exclude-bots-from-daily"]):
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
    for guild in guilds:
        if not collection("servers").find_one({"_id": guild.id}):
            collection("servers").insert_one(new_server(guild))
        rebuild_user_profiles(guild)  # check users too


def rebuild_user_profiles(guild: discord.Guild):
    '''
    Rebuilds user profiles within a given server
    '''
    for member in guild.members:
        if not collection("users").find_one(
                ufil(member, guild)):
            collection("users").insert_one(new_user(member))
