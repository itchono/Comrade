import asyncio

import discord # core to bot
from discord.ext import commands

'''
Checks
'''

# Checks

def isOwner(ctx:commands.Context):
    '''
    Determines whether message author is server owner
    '''
    return ctx.author.id == ctx.guild.owner.id

def isOP(ctx:discord.)

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
