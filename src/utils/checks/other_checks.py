import discord
from discord.ext import commands

from utils.core_dependencies.db_utils import DBcfgitem

import re

def jokeMode(ctx: commands.Context):
    '''
    Determines whether Comrade should do the small jokey things.
    '''
    try: return bool(DBcfgitem(ctx.guild.id, "joke-mode"))
    except: return True # this means that for DMs, this will automatically be true

def purgeCheck(tgt):
    '''
    Sets purge target
    '''

    def check(message: discord.Message):
        '''
        Checks whether or not to delete the message
        '''
        return message.author == tgt
    return check

def match_url(url):
    regex = re.compile(
        "(([\w]+:)?//)?(([\d\w]|%[a-fA-f\d]{2,2})+(:([\d\w]|%[a-fA-f\d]{2,2})+)?@)?([\d\w][-\d\w]{0,253}[\d\w]\.)+[\w]{2,63}(:[\d]+)?(/([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)*(\?(&?([-+_~.\d\w]|%[a-fA-f\d]{2,2})=?)*)?(#([-+_~.\d\w]|%[a-fA-f\d]{2,2})*)?"
    )
    return regex.match(url)