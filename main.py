'''
Comrade Bot - Serenity-Osprey Branch

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
from datetime import datetime # Time func

import asyncio # Dependancy for Discord py

import requests # PFP module

import random


# II: Internal Imports
import keep_alive
import comrade_cfg
import utilitymodules


'''
Initialization Phase

- Load env variables
- Declare client
- Load internal variables from DB

'''
print('Comrade is currently starting up...')
t_start = datetime.utcnow() # start time

# I: Variable Loading
dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN')
GUILD_ID = os.environ.get('GUILD')
MONGO_DRIVER = os.environ.get('DB')

cfg = comrade_cfg.data # load config variables

# Temporary Variables
vaultCandidates = {}
hando_list = {}

# II: Client startup
client = discord.Client()
bot = commands.Bot(command_prefix="$comrade")

'''
FUNCTIONS
'''

def writeInfo():
    '''
    Writes changes made to cfg dictionary to configuration file.
    '''
    if os.path.exists("comrade_cfg.py"):
        os.remove("comrade_cfg.py")
        with open("comrade_cfg.py", "w") as f:
            f.write("{} = {}\n".format("data", cfg))
        # announce to log channel
        await log("Data Written Successfully.")
    else:
        await log("Data could not be written.")

def lastDaily():
    '''
    returns last_daily in more compact syntax
    '''
    return datetime.strptime(cfg["LAST_DAILY"], "%Y-%m-%d")

async def log(msg):
    '''
    Logs stuff into preferred log channel.
    '''
    await client.get_guild(419214713252216848).get_channel(446457522862161920).send(msg)

async def dailyMSG(force = False):
    '''
    Daily routine at 7 AM EST. Used to make announcement and some others.
    Can be force called.
    '''
    await client.wait_until_ready()
    
    while not client.is_closed():

        if (datetime.utcnow().date > lastDaily() and datetime.utcnow().hour == 12) or force:
            await client.get_guild(419214713252216848).get_channel(419214713755402262).send('Good morning everyone!\nToday is {}. Have a prosperous day! <:FeelsProsperousMan:419256328465285131>'.format(datetime.utcnow().date()))
            cfg["LAST_DAILY"] = str(datetime.utcnow().date())
            writeInfo()
            await log("Daily Announcement Made. Current LAST_DAILY = {}".format(cfg["LAST_DAILY"]))
        await asyncio.sleep(60)

async def setKick():
    '''
    Generates/Regenerates kicklist for all members on server
    '''
    for member in client.get_guild(419214713252216848).members:
        cfg["kickVotes"][member.id] = []
    await log("Kicklist regenerated.")

async def quarantine(user:discord.user):
    '''
    (user object)

    Quarantines or unquarantines a user.
    '''
    currRoles = user.roles
    isQ = False
    for r in currRoles:
        if r.id == 613106246874038274: # quarantine role
            isQ = True
            currRoles.remove(r)
            # remove the role if quarantined
        elif r.id == 419215295232868361: # regular role
            currRoles.remove(r)

async def sentinelFilter(message:discord.message):
    '''
    Sentinel message filtering system, allows for multivalent toggles
    '''

    # Stage 1: text detection
    query = re.sub('\W+','', unidecode.unidecode(message.content.lower())) # clean message content down to text
    
    strict = message.author.id in cfg["THREATS"] and cfg["THREATS"][message.author.id] >= 2


    for word in set(cfg["GLOBAL_BANNED_WORDS"]).union(set(cfg["THREATS"][message.author.id] if message.author.id in cfg["THREATS"] else set())):
        if word in query or (fuzz.partial_ratio(word, query) > 75 and strict):
            await message.delete()
            await log('Message purged for bad word:\n'+ str(message.content))
            
            #await infraction(message, message.author.id, 0.5)

    # Stage 2: Emoji backfiltering

'''
COMMANDS
'''

@bot.event
async def status(ctx):
    await ctx.send("OK")

# create server
'''keep_alive.keep_alive()'''
# create tasks
'''client.loop.create_task(dailyMSG())'''

# finally, start the bot
'''client.run(TOKEN)'''

if __name__ == "__main__":
    cfg["LETHALITY"] = 1
    writeInfo()
