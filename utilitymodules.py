'''
Comrade Bot - Additional Utility Modules

'''

# I: External Library Imports
import discord # core to bot
from discord.ext import commands
import pymongo # CFG storage

# Text Filtering
import re
import unidecode
from fuzzywuzzy import fuzz # ALSO: need python-levenshtein ==> needs C++ build tools installed

# File reading for env vars
import os
import dotenv # NOTE - install as "pip install python-dotenv"

# Misc stuff
from datetime import datetime # Time func

import asyncio # Dependancy for Discord py

import requests # PFP module

import random

async def generateRequiem(message: discord.message, mode='NonRole'):
    # produces a list of members to be purged

    if mode == 'NonRole':
        # produces a list of members to be purged
        # takes in server

        non_roled = []
        for member in message.guild.members:
            if str(member.roles) == '[<Role id=419214713252216848 name=\'@everyone\'>, <Role id=419215295232868361 name=\'Communism is the only Role\'>]':
                non_roled.append(member)
        
        names = []
        for member in non_roled:
            names.append(str(member))
        await message.channel.send('Preliminary List of members without other roles:')
        await message.channel.send(str(names))

        await message.channel.send('Trimming. This will take a while.')
        for channel in message.guild.text_channels:
            async for msg in channel.history(limit=None,after=datetime.datetime(2019, 10, 8)):
                for member in non_roled:
                    if msg.author == member:
                        await message.channel.send(str('Member found: {0} in message sent at {1}:\n{2}'.format(non_roled.pop(non_roled.index(member)), str(msg.created_at), msg.content)))

        return non_roled
    elif mode == 'All':
        # takes in server

        members = []
        for member in message.guild.members:
            members.append(member)

        await message.channel.send('Scanning ALL members This will take a while.')
        for channel in message.guild.text_channels:
            async for msg in channel.history(limit=None,after=datetime.datetime(2019, 10, 8)):
                for member in members:
                    if msg.author == member:
                        members.remove(member)

        return members

def makeLookUpTable():
    '''
    makes the lookup table for emojis
    '''

    s = "{}"

    for i in range(127462, 127488):
        s += "u\\U"
        s += "000"
        s += str(hex(i))[2:].upper()


def emojiToText(s):
    '''
    Converts emoji to closest real text representation
    '''
    lookupTable = {u"\U0001F1E6"}