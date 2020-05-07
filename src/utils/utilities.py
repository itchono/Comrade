import asyncio

import discord # core to bot
from discord.ext import commands
from utils.mongo_interface import *

import requests

'''
Checks
'''

# Checks

def isOwner(ctx:commands.Context):
    '''
    Determines whether message author is server owner
    '''
    return ctx.author.id == ctx.guild.owner.id

def isOP(ctx:commands.Context):
    '''
    Determines whether message author is an OP
    '''
    OPS = userQuery({"OP":True})

    for op in OPS:
        if ctx.author.id == op["_id"]:
            return True
    return False

def isnotThreat(ctx:commands.Context):
    '''
    Determines whether message author is a threat
    '''
    OPS = userQuery({"threat level":{"$gt":0}})

    for op in OPS:
        if ctx.author.id == op["_id"]:
            return False
    return True

'''
Message Helpers
'''

async def delSend(s:str, channel:discord.TextChannel, time:int = 10):
    '''
    Sends a message to the desired channel, with a deletion option after a fixed time, default 10 seconds.
    Standard sending module for Comrade
    '''
    msg = await channel.send(s)
    await asyncio.sleep(time)
    await msg.add_reaction("🗑️")

async def timedSend(s:str, channel:discord.TextChannel, time:int = 10):
    '''
    Sends a message to the desired channel, with deletion after a fixed time, default 10 seconds.
    '''
    msg = await channel.send(s)
    await asyncio.sleep(time)
    await msg.delete()

'''
Image Extractor
'''

async def getavatar(member:discord.Member):
    '''
    Returns file bytes of avatar
    '''
    r = requests.get(member.avatar_url)
    with open("avatars/{}.png".format(member.id), "wb") as f:
        f.write(r.content)
    return r.content

async def doppel(member:discord.Member):
    pass