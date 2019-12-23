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
from fuzzywuzzy import fuzz # ALSO: need python-levenshtein ==> needs C++ build tools installed

# File reading for env vars
import os
import dotenv # NOTE - install as "pip install python-dotenv"

# Misc stuff
import datetime # Time func

import asyncio # Dependancy for Discord py

import requests # PFP module

import random


# II: Internal Imports
import keep_alive

# III: Core modules

'''
Initialization Phase

- Load env variables
- Declare client
- Load internal variables from DB

'''
print('Comrade is currently starting up...')
t_start = datetime.datetime.utcnow() # start time

# I: Variable Loading
dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN')
GUILD_ID = os.environ.get('GUILD')
MONGO_DRIVER = os.environ.get('DB')
print('Environment variables loaded.')

mongoClient = pymongo.MongoClient(MONGO_DRIVER) # requires dnspython
cfg = mongoClient["Comrade"]["cfg"]

def writeCFG(key, data, doc = "generalCFG"):
    '''
    Updates value in cfg database given a document id, key to modify, and new data value.
    Defaults to writing in general CFG document

    >>> writeCFG("LETHALITY", 1)
    changes LETHALITY field under generalCFG to value of 1

    >>> writeCFG(")
    '''
    cfg.update_one({"_id":doc}, {"$set":{key:data}})
for x in (cfg.find({"_id":"kickVotes"})):
    print(x)
#writeCFG(308287917556498452, list(list(cfg["kickVotes"][308287917556498452]) + [123456]), doc = "kickVotes")

# Complex Variables
kickVotes = 

# Temporary Variables
vaultCandidates = {}
hando_list = {}


# II: Client startup
client = discord.Client()
bot = commands.Bot(command_prefix="$comrade")

@bot.event
async def status(ctx):
    await ctx.send("OK")



# create server
keep_alive.keep_alive()
# create tasks
#client.loop.create_task(dailyMSG())

# finally, start the bot
# client.run(TOKEN)
