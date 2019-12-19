'''
Comrade Bot - Serenity Branch

Full Rewrite of functional components of Comrade to be more robust
Mingde Yin

December 2019 - 2020



'''

# I: External Library Imports
import discord # core to bot
from discord.ext import commands
import pymongo # CFG storage

# Text Filtering
import re
import unidecode
from fuzzywuzzy import fuzz # ALSO: need python-levenshtein

# File reading for env vars
import os
import dotenv

# Misc stuff
import datetime # Time func

import asyncio # Dependancy for Discord py

import requests # PFP module

import random


# II: Internal Imports
import comrade_cfg
from comrade_modules import *


'''
Initialization Phase

- Load env variables
- Declare client
- Load internal variables from DB

'''
print('Comrade is currently starting up...')
t_start = datetime.datetime.utcnow() # start time

# I: Variable Loading
# TODO
cfg = comrade_cfg.cfg


# Temporary Variables
vaultCandidates = {}
hando_list = {}


# II: Client startup

TOKEN = os.environ.get('TOKEN')
GUILD_ID = os.environ.get('GUILD')

client = discord.Client()
bot = commands.Bot(command_prefix="$comrade")

@bot.event
async def status(ctx):
    await ctx.send("OK")


# create server
keep_alive.keep_alive()
# create tasks
client.loop.create_task(dailyMSG())

# finally, start the bot
client.run(TOKEN)