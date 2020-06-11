import discord  # core to bot
from discord.ext import commands, tasks

from utils.mongo_interface import *
from cfg import *

import requests
import asyncio
import random
import datetime
import time
import pytz
import string
import socket

'''
Checks
'''

# TODO cache OPs, Threats, etc

def isOwner(ctx: commands.Context):
    '''
    Determines whether message author is server owner
    '''
    return ctx.guild and (ctx.author.id == ctx.guild.owner.id or DEVELOPMENT_MODE) # TODO check owner-only cmds for DMs

def isOP(ctx: commands.Context):
    '''
    Determines whether message author is an OP
    '''
    if not ctx.guild: return True
    return ctx.author.id in [i["user"] for i in getOPS(ctx.guild.id)]

def isnotThreat(ctx: commands.Context):
    '''
    Determines whether message author is a threat
    '''
    if not ctx.guild: return True
    return not ctx.author.id in [i["user"] for i in getThreats(ctx.guild.id) if i["threat level"] > 0]

def isnotSuperThreat(ctx: commands.Context):
    '''
    Determines whether message author is threat level >1
    '''
    if not ctx.guild: return True
    return not ctx.author.id in [i["user"] for i in getThreats(ctx.guild.id) if i["threat level"] > 1]


def isnotUltraThreat(ctx: commands.Context):
    '''
    Determines whether message author is threat level >2
    '''
    if not ctx.guild: return True
    return not ctx.author.id in [i["user"] for i in getThreats(ctx.guild.id) if i["threat level"] > 2]

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

async def DM(s: str, user: discord.User, embed=None):
    '''
    DMs a person
    '''
    userChannel = await user.create_dm()
    await userChannel.send(content=s, embed=embed)

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
    try:
        tgt = tgt.strip("\"")
        
        if ctx.guild:
            try: return await commands.MemberConverter().convert(ctx, tgt)
            except:
                try: return await commands.MemberConverter().convert(ctx, string.capwords(tgt))
                except: await ctx.send("Member with input '{}' could not be found.".format(tgt))
        else:
            try: return await commands.UserConverter().convert(ctx, tgt)
            except:
                try: return await commands.UserConverter().convert(ctx, string.capwords(tgt))
                except: await ctx.send("User with input '{}' could not be found.".format(tgt))
    except: pass

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
    #print("LOG [{}] {} -- {}".format(guild.name, localTime().strftime("%I:%M:%S %p %Z"), m)) # for testing
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
Roles
'''

async def dailyRole(guild: discord.Guild):
    '''
    Returns the Comrade "Member of the Day" role for a guild, if it exists, or creates it
    '''
    for role in guild.roles:
        if role.name == "Member of the Day":
            return role
    
    return await guild.create_role(name="Member of the Day", colour=discord.Colour.from_rgb(*DAILY_MEMBER_COLOUR), mentionable=True)

async def mutedRole(guild: discord.Guild):
    '''
    Returns the Comrade "Comrade-Mute" role for a guild, if it exists, or creates it
    '''
    for role in guild.roles:
        if role.name == "Comrade-Mute":
            return role
    
    return await guild.create_role(name="Comrade-Mute")

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