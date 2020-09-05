import discord
from discord.ext import commands

from utils.core_dependencies.db_utils import getThreats, getOPS

def isOP(ctx: commands.Context):
    '''
    Determines whether message author is an OP
    '''
    if not ctx.guild: return True
    return ctx.author.id in [i["user"] for i in getOPS(ctx.guild.id)]

def isNotThreat(threatLevel:int = 0):
    '''
    Returns a function that checks of the message author is of a certain threat-level or higher
    '''
    def ret(ctx: commands.Context):
        if not ctx.guild: return True
        return not ctx.author.id in [i["user"] for i in getThreats(ctx.guild.id) if i["threat-level"] > threatLevel]
    return ret

def isServerOwner():
    def predicate(ctx: commands.Context):
        '''
        Determines whether message author is server owner
        '''
        return ctx.guild and (ctx.author.id == ctx.guild.owner.id or DEVELOPMENT_MODE)
    return commands.check(predicate)

def isUser(name:str):
    
    def predicate(ctx: commands.Context):
        '''
        Determines whether message author bears the name.
        '''
        return ctx.author.name == name
    return commands.check(predicate)

