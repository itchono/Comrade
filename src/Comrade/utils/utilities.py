import discord

import time
import pytz
import datetime
import socket
from urllib.parse import urlparse

from config import cfg


bot_prefix = cfg["Settings"]["prefix"].strip("\"")
startup_time = None


def set_start_time(time):
    '''
    Sets the startup time for the bot,
    so that we can use it to calculate the uptime of the bot
    '''
    global startup_time
    startup_time = time


def get_uptime() -> float:
    '''
    Returns uptime in seconds.
    '''
    return time.perf_counter() - startup_time


def local_time() -> datetime.datetime:
    '''
    Returns local time.
    '''
    utc = pytz.timezone("UTC").localize(datetime.datetime.utcnow())
    return utc.astimezone(pytz.timezone(cfg["Settings"]["timezone"]))


def utc_to_local_time(t) -> datetime.datetime:
    '''
    Converts UTC to local time
    '''
    utc = pytz.timezone("UTC").localize(t)
    return utc.astimezone(pytz.timezone(cfg["Settings"]["timezone"]))


def get_host() -> str:
    '''
    Gets the name of the host.
    '''
    try:
        host_name = socket.gethostname()
        return str(host_name)
    except Exception as ex:
        return str(ex)


def webscrape_header() -> dict:
    '''
    Returns user agent and header, useful for web scraping
    '''
    user_agent = ('Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7)'
                  ' Gecko/2009021910 Firefox/3.0.7')
    return {'User-Agent': user_agent, }


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def ufil(member: discord.Member) -> dict:
    # Conveience method to get filter when querying user collection
    return {"user": member.id, "server": member.guild.id}


async def role(guild: discord.Guild, name: str):
    '''
    Returns the named role for a guild,
    if it exists, or tries to create it
    '''
    if role := discord.utils.find(
            lambda role: role.name == name, guild.roles):
        return role
    try:
        role = await guild.create_role(name=name, mentionable=True)
    except discord.errors.Forbidden:
        return None
