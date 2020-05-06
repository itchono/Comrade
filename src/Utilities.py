import asyncio

import discord # core to bot
from discord.ext import commands

'''
Checks
'''

# Checks

def isOwner(ctx:discord.Guild):
    '''
    Determines whether message author is server owner
    '''
    return ctx.author.id == ctx.guild.owner.id

'''
Message Helpers
'''

async def delSend(s:str, channel:discord.TextChannel):
    '''
    Sends a message to the desired channel, with a deletion option after 10 seconds.
    Standard sending module for Comrade
    '''
    msg = await channel.send(s)
    await asyncio.sleep(10)
    await msg.add_reaction("🗑️")