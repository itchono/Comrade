import asyncio

import discord  # core to bot
from discord.ext import commands, tasks
from utils.mongo_interface import *

import requests
import random
import datetime
import pytz

import string

import socket

DEVELOPMENT_MODE = False
# set to true for pre-testing.

LOCAL_TIMEZONE = 'Canada/Eastern'
# change depending on host.

BOT_PREFIX = "$c "

DEFAULT_DAILY_COUNT = 2
# amount of daily member counts everyone starts with


'''
Checks
'''

# Checks

def isOwner(ctx: commands.Context):
    '''
    Determines whether message author is server owner
    '''
    return ctx.author.id == ctx.guild.owner.id or DEVELOPMENT_MODE

def isServer(ctx: commands.Context):
    '''
    Determines whether message was called in a server
    '''
    return (ctx.guild is not None)

def isOP(ctx: commands.Context):
    '''
    Determines whether message author is an OP
    '''
    OPS = userQuery({"OP": True})

    for op in OPS:
        if ctx.author.id == op["user"]:
            return True
    return False


def isUserOP(user: discord.User):
    '''
    Determines whether message author is an OP
    '''
    OPS = userQuery({"OP": True})

    for op in OPS:
        if user.id == op["user"]:
            return True
    return False


def isnotThreat(ctx: commands.Context):
    '''
    Determines whether message author is a threat
    '''
    if not ctx.guild: return True

    OPS = userQuery({"threat level": {"$gt": 0}, "server": ctx.guild.id})

    for op in OPS:
        if ctx.author.id == op["user"]:
            return False
    return True

def isnotSuperThreat(ctx: commands.Context):
    '''
    Determines whether message author is threat level 2 or higher
    '''
    if not ctx.guild: return True

    OPS = userQuery({"threat level": {"$gte": 2}, "server": ctx.guild.id})

    for op in OPS:
        if ctx.author.id == op["user"]:
            return False
    return True

def isnotUltraThreat(ctx: commands.Context):
    '''
    Determines whether message author is threat level 3 or higher
    '''
    if not ctx.guild: return True

    OPS = userQuery({"threat level": {"$gte": 3}, "server": ctx.guild.id})

    for op in OPS:
        if ctx.author.id == op["user"]:
            return False
    return True


purgeTGT = None
def setTGT(tgt):
    '''
    Sets purge target
    '''
    global purgeTGT
    purgeTGT = tgt


def purgeCheck(message: discord.Message):
    '''
    Checks whether or not to delete the message
    '''
    return message.author == purgeTGT


def isWebhook(message: discord.Message):
    '''
    Checks if it's a webhook
    '''
    return message.author.discriminator == "0000"


def isCommand(message: discord.Message):
    '''
    Check's if it's a Comrade Command
    '''
    return BOT_PREFIX in message.content.lower()


'''
Message Helpers
'''
async def delSend(s: str, channel: discord.TextChannel, time: int = 5):
    '''
    Sends a message to the desired channel, with a deletion option after a fixed time, default 5 seconds.
    Standard sending module for Comrade
    '''
    msg = await channel.send(s)
    await asyncio.sleep(time)
    await msg.add_reaction("🗑️")


async def timedSend(s: str, channel: discord.TextChannel, time: int = 10):
    '''
    Sends a message to the desired channel, with deletion after a fixed time, default 10 seconds.
    '''
    msg = await channel.send(s)
    await asyncio.sleep(time)
    await msg.delete()


async def reactOK(ctx: commands.Context):
    '''
    Adds reaction to show that task was completed successfully.
    '''
    await ctx.message.add_reaction("👍")

async def reactX(ctx: commands.Context):
    '''
    Adds reaction to show that task was forbidden.
    '''
    await ctx.message.add_reaction("❌")


async def reactQuestion(ctx: commands.Context):
    '''
    Adds reaction to show that something went wrong
    '''
    await ctx.message.add_reaction("❓")


async def DM(s: str, member: discord.Member, embed=None):
    '''
    DMs a person
    '''
    memberChannel = await member.create_dm()
    await memberChannel.send(content=s, embed=embed)


'''
Image Extractor
'''


async def getavatar(member: discord.Member):
    '''
    Returns file bytes of avatar
    '''
    r = requests.get(member.avatar_url)
    return r.content


'''
Converters and Stuff
'''


async def extractUser(ctx: commands.Context, tgt: str):
    '''
    Returns a server member or user; based on display name in server, user ID, or by mention.
    '''
    if not tgt:
        return None
    elif ctx.guild:
        try:
            return await commands.MemberConverter().convert(ctx, tgt)
        except:
            try:
                return await commands.MemberConverter().convert(ctx, string.capwords(tgt))
            except:
                await ctx.send("Member with input '{}' could not be found.".format(tgt))
                return None
    else:
        try:
            return await commands.UserConverter().convert(ctx, tgt)
        except:
            try:
                return await commands.UserConverter().convert(ctx, string.capwords(tgt))
            except:
                await ctx.send("User with input '{}' could not be found.".format(tgt))
                return None


async def getChannel(guild: discord.Guild, name: str):
    '''
    Gets a channel in a server, given a NAME of the channel; uses mongoDB cfg file. 
    '''
    c = guild.get_channel(getCFG(guild.id)[name])
    
    if not c:
        if name != "log channel":
            await log(guild, "Channel not found.")
        else:
            print("Error: (Log Channel not set up); channel not found")
    return c


'''
logger
'''


async def log(guild, m: str, embed=None):
    '''
    Logs a message in the server's log channel in a clean embed form, or sends a pre-made embed.
    '''
    lgc = await getChannel(guild, "log channel")
    if not embed:
        embed = discord.Embed(title="Log Entry", description=m)
        embed.add_field(name="Time", value=(localTime().strftime("%I:%M:%S %p %Z")))
    await lgc.send(embed=embed)

def getHost(): 
    '''
    Gets the name of the host.
    '''
    try: 
        host_name = socket.gethostname() 
        return "{}".format(host_name)
    except: 
        return "IP could not be determined."

'''
Misc
'''

def localTime(zone=LOCAL_TIMEZONE):
    '''
    Returns local time based on some input TZ.
    '''
    utc = pytz.timezone("UTC").localize(datetime.datetime.utcnow())
    return utc.astimezone(pytz.timezone(LOCAL_TIMEZONE))

def UTCtoLocalTime(t, zone=LOCAL_TIMEZONE):
    '''
    Converts UTC to local time
    '''
    utc = pytz.timezone("UTC").localize(t)
    return utc.astimezone(pytz.timezone(LOCAL_TIMEZONE))