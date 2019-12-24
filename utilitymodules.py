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
    PURGE_DATE = datetime.datetime(2099, 1, 1)
    # SET this first

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
            async for msg in channel.history(limit=None,after=PURGE_DATE):
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
            async for msg in channel.history(limit=None,after=PURGE_DATE):
                for member in members:
                    if msg.author == member:
                        members.remove(member)
        return members

def makeLookUpTable(textToEmoji=False):
    '''
    Makes the lookup table for emojis
    '''
    s = "{"
    if textToEmoji:
        for i in range(127462, 127488):
            s += "\""
            s += chr(i-127365)
            s += "\":u\"\\U000"
            s += str(hex(i))[2:].upper()
            s += "\","
    else:
        for i in range(127462, 127488):
            s += "u\"\\U=000"
            s += str(hex(i))[2:].upper()
            s += "\":\"{}\",".format(chr(i-127365))
    s += "}"
    print(s)

def emojiToText(s):
    '''
    Converts emoji to closest real text representation (lowercase output)
    '''
    lookupTable = {u"\U0001F1E6":"a",u"\U0001F1E7":"b",u"\U0001F1E8":"c",u"\U0001F1E9":"d",u"\U0001F1EA":"e",u"\U0001F1EB":"f",u"\U0001F1EC":"g",u"\U0001F1ED":"h",u"\U0001F1EE":"i",u"\U0001F1EF":"j",u"\U0001F1F0":"k",u"\U0001F1F1":"l",u"\U0001F1F2":"m",u"\U0001F1F3":"n",u"\U0001F1F4":"o",u"\U0001F1F5":"p",u"\U0001F1F6":"q",u"\U0001F1F7":"r",u"\U0001F1F8":"s",u"\U0001F1F9":"t",u"\U0001F1FA":"u",u"\U0001F1FB":"v",u"\U0001F1FC":"w",u"\U0001F1FD":"x",u"\U0001F1FE":"y",u"\U0001F1FF":"z"}

    newS = ''
    for c in s:
        if c in lookupTable:
            newS += lookupTable[c]
        else:
            newS += c
    return newS

def textToEmoji(s):
    '''
    Converts text to equivalent emoji
    '''
    lookupTable = {"a":u"\U0001F1E6","b":u"\U0001F1E7","c":u"\U0001F1E8","d":u"\U0001F1E9","e":u"\U0001F1EA","f":u"\U0001F1EB","g":u"\U0001F1EC","h":u"\U0001F1ED","i":u"\U0001F1EE","j":u"\U0001F1EF","k":u"\U0001F1F0","l":u"\U0001F1F1","m":u"\U0001F1F2","n":u"\U0001F1F3","o":u"\U0001F1F4","p":u"\U0001F1F5","q":u"\U0001F1F6","r":u"\U0001F1F7","s":u"\U0001F1F8","t":u"\U0001F1F9","u":u"\U0001F1FA","v":u"\U0001F1FB","w":u"\U0001F1FC","x":u"\U0001F1FD","y":u"\U0001F1FE","z":u"\U0001F1FF"}

    s = s.lower()

    newS = ''
    for c in s:
        if c in lookupTable:
            newS += lookupTable[c]
        else:
            newS += c
    return newS

