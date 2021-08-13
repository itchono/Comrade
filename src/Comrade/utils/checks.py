from discord.ext import commands

from functools import lru_cache
from db import collection
from utils.logger import logger


@lru_cache()
def op_list(guild_id: int):
    '''
    Returns list of OPS in a server
    '''
    all_users = collection("users").find(
        {"server": guild_id,
         "OP": True})
    return [u["user"] for u in all_users]


@lru_cache()
def threat_list(guild_id: int, threat_level: int):
    '''
    Returns list of threats ids in a given server
    '''
    all_users = collection("users").find(
        {"server": guild_id,
         "moderation.threat-level": {"$gt": threat_level - 1}})
    return [u["user"] for u in all_users]


def isOP():
    '''
    Returns a function that checks of the message
    author is an OP
    '''
    def predicate(ctx: commands.Context):
        if not ctx.guild:
            return True
        ops = op_list(ctx.guild.id)
        logger.debug(
            f"OP Check for {ctx.author.id}\nCache Status: {op_list.cache_info()}")
        return ctx.author.id in ops
    return predicate


def isNotThreat(threat_level: int = 1):
    '''
    Returns a function that checks of the message
    author is of a certain threat-level or higher
    '''
    def predicate(ctx: commands.Context):
        if not ctx.guild:
            return True
        threats = threat_list(ctx.guild.id, threat_level)
        logger.debug(
            f"Threat Check for {ctx.author.id}\nCache Status: {threat_list.cache_info()}")
        return ctx.author.id not in threats
    return predicate


def isServerOwner():
    def predicate(ctx: commands.Context):
        '''
        Determines whether message author is server owner
        '''
        return ctx.guild and ctx.author.id == ctx.guild.owner.id
    return commands.check(predicate)
