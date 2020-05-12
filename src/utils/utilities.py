import asyncio

import discord # core to bot
from discord.ext import commands
from utils.mongo_interface import *

import requests
import random

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

purgeTGT = None

def purgeCheck(message:discord.Message):
    '''
    Checks whether or not to delete the message
    '''
    return message.author == purgeTGT

def isWebhook(message:discord.Message):
    '''
    Checks if it's a webhook
    '''
    return message.author.discriminator == "0000"

def isCommand(message:discord.Message):
    '''
    Check's if it's a Comrade Command
    '''
    return "$c" in message.content.lower()


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

async def DM(s:str, member:discord.Member):
    '''
    DMs a person
    '''
    memberChannel = await member.create_dm()
    await memberChannel.send(s)


'''
Image Extractor
'''

async def getavatar(member:discord.Member):
    '''
    Returns file bytes of avatar
    '''
    r = requests.get(member.avatar_url)
    return r.content

'''
Converters and Stuff
'''

async def extractUser(bot: commands.Bot, ctx: commands.Context, tgt: str):
    '''
    Returns a server member or user; based on display name in server, user ID, or by mention.
    '''
    if not tgt: 
        return None

    u = getUserfromNick(tgt)
    if tgt.isnumeric():
        # if user ID
        u = {"_id":int(tgt)}
    elif not u:
        # if mention
        u = {"_id":int(tgt[3:-1])} if tgt[3:-1].isnumeric() else None

    if u:
        return ctx.guild.get_member(u["_id"]) if ctx.guild else bot.get_user(u["_id"])
    else:
        await ctx.send("Unable to find user with input {}".format(tgt))
        return None



