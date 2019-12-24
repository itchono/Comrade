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

PROTECTED_NAMES = ["LETHALITY", "THREATS", "kickVotes", "OPS", "GLOBAL_BANNED_WORDS", "PURGE", "LAST_DAILY"]
# Protected dictionary elements in cfg file

# Temporary Variables
vaultCandidates = {}
hando_list = {}

# II: Client startup
client = discord.Client()
bot = commands.Bot(command_prefix="$comrade") # declare bot with prefix $comrade

'''
FUNCTIONS
'''
async def log(msg):
    '''
    Logs stuff into preferred log channel.
    '''
    await client.get_guild(419214713252216848).get_channel(446457522862161920).send(msg)

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

def reloadVars():
    '''
    Reloads variables from configuration file dynamically if needed
    '''
    global cfg
    cfg = comrade_cfg.data
    log("Variables Successfully Reloaded From File.")

def lastDaily():
    '''
    returns last_daily in more compact syntax
    '''
    return datetime.strptime(cfg["LAST_DAILY"], "%Y-%m-%d")

async def cleanMSG():
    '''
    Removes all bot messages in the last 24 hours.
    '''
    for channel in client.get_guild(419214713252216848).text_channels:
        yesterday = datetime.datetime.now()-datetime.timedelta(days=1)
        async for msg in channel.history(limit=None,after=yesterday):
            if msg.author == client.user:
                await msg.delete()

async def dailyRole():
    '''
    Sets new daily member, removing all previous daily member roles
    '''

    members = client.get_guild(419214713252216848).members
    random.seed()
    chosenone = random.randint(0, len(members)-1)

    s = members[chosenone].name

    for member in client.get_guild(419214713252216848).members:
        currRoles = member.roles
        for r in currRoles:
            if r.id == 655670092679479296: # Daily
                currRoles.remove(r)
                await member.edit(roles=currRoles)
                # remove the role if Daily'd
        if member == members[chosenone]:
            currRoles.append(client.get_guild(419214713252216848).get_role(655670092679479296))
            await member.edit(roles=currRoles)
            await client.get_guild(419214713252216848).get_channel(419214713755402262).send('Today\'s daily member is {}'.format(s))

async def dailyMSG(force = False):
    '''
    Daily routine at 7 AM EST. Used to make announcement and some others.
    Can be force called.
    '''
    await client.wait_until_ready()
    
    while not client.is_closed():
        if (datetime.utcnow().date > lastDaily() and datetime.utcnow().hour == 12) or force:
            await cleanMSG()
            asyncio.sleep(30)
            # allow 30 seconds for script to run to clean messages

            await client.get_guild(419214713252216848).get_channel(419214713755402262).send('Good morning everyone!\nToday is {}. Have a prosperous day! <:FeelsProsperousMan:419256328465285131>'.format(datetime.utcnow().date()))
            cfg["LAST_DAILY"] = str(datetime.utcnow().date())
            writeInfo()
            await log("Daily Announcement Made. Current LAST_DAILY = {}".format(cfg["LAST_DAILY"]))
            # make announcement

            dailyRole() # do daily role
        await asyncio.sleep(60)

async def genKick():
    '''
    Generates/Regenerates kicklist for all members on server
    '''
    for member in client.get_guild(419214713252216848).members:
        cfg["kickVotes"][member.id] = []
    
    writeInfo()
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
    if isQ:
        currRoles.append(client.get_guild(419214713252216848).get_role(419215295232868361))
        await log("User Released: {}".format(user.name))
        return '{} has been returned to society.'.format(user.name)
    else:
        currRoles.append(client.get_guild(419214713252216848).get_role(613106246874038274))
        await log("User Quarantined: {}".format(user.name))
        return '{} has been quarantined.'.format(user.name)
    await user.edit(roles=currRoles)

async def sentinelFilter(message:discord.message):
    '''
    Sentinel message filtering system, allows for multivalent toggles
    '''
    # Stage 1: text detection
    query = re.sub('\W+','', unidecode.unidecode(utilitymodules.emojiToText(message.content.lower()))) # clean message content down to text
    # 3 Stages of filtering: 1) Emoji pass through 2) Eliminating nonstandard unicode chars 3) Regex Substitutions to eliminate non word characters
    
    strict = (message.author.id in cfg["THREATS"] and cfg["THREATS"][message.author.id] >= 3) or cfg["LETHALITY"] >= 3 # determines whether message filtering should be relaxed (needs exact content) or strict (75% match)
    superStrict = (message.author.id in cfg["THREATS"] and cfg["THREATS"][message.author.id] >= 4) or cfg["LETHALITY"] >=3 # even more strict filtering when needed

    for word in set(cfg["GLOBAL_BANNED_WORDS"]).union(set(cfg["THREATS"][message.author.id] if message.author.id in cfg["THREATS"] else set())):
        # checks every banned word for that user
        if word in query or (len(query) > 2 and strict and fuzz.partial_ratio(word, query) > 65):
            # passes query through fuzzy filtering system IF length of word is long enough and author is subhect to strict filtering
            await message.delete()
            await log('Message purged for bad word:\n'+ str(message.content) + "\nsent by " + str(message.author.name))
    
    # Stage 2: Attachment Filtering
    if strict and (len(message.attachments) > 0 or len(message.embeds) > 0):
        await message.delete()
        await log('Message purged for embed; sent by ' + str(message.author.name))

    # Stage 3: Ping Filtering
    if superStrict and len(message.mentions) > 0:
        await message.delete()
        await message.channel.send("USELESS PING DETECTED SENT BY {}".format(message.author.mention))

# TODO new infraction System?

'''
COMMANDS
'''

# Checks
def isOP(ctx):
    '''
    Determines whether message author is OP
    '''
    return ctx.author.id in cfg["OPS"]

def isOwner(ctx):
    '''
    Determines whether message author is server owner
    '''
    OWNER_ID = 66137108124803072
    return ctx.author.id == OWNER_ID

def notThreat(ctx):
    '''
    Determines whether message author is in good standing
    (Either not a threat or at threat level zero)
    '''
    return (not ctx.author.id in cfg["THREATS"] or cfg["THREATS"][ctx.author.id]["LETHALITY"] == 0)

async def addKick(ctx, user):
    '''
    Generalized manner of adding a voteKick to a user. Helper function for voteKick command.
    '''
    cfg["kickVotes"][user].append(ctx.author.id) # Add vote
    num_votes = len(cfg["kickVotes"][user])
    writeInfo()
    await ctx.send("Vote added for {0} ({1}/{2}).".format(user.name, num_votes, cfg["KICK_REQ"]))

    # Check if threshold is met
    if num_votes >= cfg["KICK_REQ"]:
        if cfg["LETHALITY"] >= 1:
            await ctx.send("Kicking {}...".format(user.name))
            await ctx.guild.kick(user)
            genKick() # regen list
        else:
            await ctx.send("Kicking has been disabled. Lethality must be at least 1 to continue (current = {}).".format(cfg["LETHALITY"]))

# Kick System
@bot.command()
async def voteKick(ctx):
    '''
    Checks to see whether to add vote to kick a user.
    '''
    user = ctx.message.mentions[0]
    if ctx.author.id in cfg["kickVotes"][user.id]:
        await ctx.send("You have already voted!")
    elif user.id in cfg["KICK_SAFE"]:
        await ctx.send("Target is in Kick Safe list!")
    elif ctx.author.id in cfg["THREATS"] and cfg["THREATS"][ctx.author.id] >= 1:
        await ctx.send("Due to you being a threat, you are not allowed to vote!")
    else:
        await addKick(ctx, user)

@bot.command()
async def unKick(ctx):
    '''
    Removes vote from user.
    '''
    user = ctx.message.mentions[0]
    if ctx.author.id in cfg["kickVotes"][user.id]:
        cfg["kickVotes"][user.id].remove(ctx.author.id)
        num_votes = len(cfg["kickVotes"][user])
        writeInfo()
        await ctx.send("Vote removed for {0} ({1}/{2}).".format(user.name, num_votes, cfg["KICK_REQ"]))
    else:
        await ctx.send("You have not voted to kick {}.".format(user.name))

'''
LETHALITY SYSTEM

Global: Enables and disables features at various levels
0: None
1: Kicking enabled
2: Message Filtering for threats enabled
3: Message filtering for all users enabled
4: Purge enabled

Per user: Subjects users in THREATS list to stricter conditions; subject to limitation by global lethality
0: No restrictions
1: No voting of any form
2: Messages filtered (relaxed)
3: Messages filtered strictly
4: Loss of ability to ping
'''
# General Moderation Methods
@bot.command(name = "lethal")
@commands.check(isOP)
async def setLethality(ctx, Lnew):
    '''
    Changes lethality level either for user, or globally
    '''
    if float(Lnew) >= 0:
        # safety check for level

        # Global Modificaiton
        if len(ctx.message.mentions) == 0:
            cfg["LETHALITY"] = float(Lnew)
            writeInfo()
            await ctx.send("Global Lethality has been set to {}.".format(cfg["LETHALITY"]))
        # Modificaiton for a single user (in THREATS)
        else:
            user = ctx.message.mentions[0]
            if user.id in cfg["THREATS"]:
                cfg["THREATS"][user.id]["LETHALITY"] = float(Lnew)
                writeInfo()
                await ctx.send("User Lethality has been set to {}.\nPlease ensure global lethality is set accordingly to enable lethal features.".format(cfg["LETHALITY"]))
    else:
        await ctx.send("Invalid Input.")

@bot.command(name = "kickReq")
@commands.check(isOP)
async def setKickReq(ctx, Knew):
    if int(Knew) >= 1:
        cfg["KICK_REQ"] = int(Knew)
        writeInfo()
        await ctx.send("Kick Requirement Set to {} votes.".format(cfg["KICK_REQ"]))
    else:
        await ctx.send("Invalid input.")

@bot.command(name = "quarantine")
@commands.check(isOP)
async def callQuarantine(ctx):
    '''
    Quarantines mentioned user
    '''
    user = ctx.message.mentions[0]
    await ctx.send(quarantine(user))

#@bot SCRAM

# Threat dictionary methods
@bot.command()
@commands.check(isOP)
async def addThreat(ctx, *args):
    '''
    Adds user to threats list with or without a preset lethality level (default: 3)
    '''
    level = args[0] if len(args) > 0 else 3 # ternary assignment to use as default parameter
    user = ctx.message.mentions[0]
    if not user.id in cfg["THREATS"]:
        cfg["THREATS"][user.id] = {"LETHALITY":level, "BANNED_WORDS":set()}
        writeInfo()
        await ctx.send("Threat Added with Lethality = {}".format(cfg["THREATS"][user.id]["LETHALITY"]))

@bot.command()
@commands.check(isOP)
async def removeThreat(ctx):
    '''
    Removes target user from threats list.
    '''
    user = ctx.message.mentions[0]
    if user.id in cfg["THREATS"]:
        del cfg["THREATS"][user.id]
        writeInfo()
        await ctx.send("Threat removed.")

@bot.command()
@commands.check(isOP)
async def addBanWord(ctx, word):
    '''
    Adds a banned word, either to the global set or to a particular user.
    Use "" Quotes to enclose larger phrases
    '''
    if len(ctx.message.mentions) == 0 and not word.lower() in cfg["GLOBAL_BANNED_WORDS"]:
        # global
        cfg["GLOBAL_BANNED_WORDS"].add(word.lower())
        writeInfo()
        await ctx.send("{} Has been added to the global blacklist.".format(word.lower()))
    else:
        user = ctx.message.mentions[0]
        if user.id in cfg["THREATS"] and not word.lower() in cfg["THREATS"][user.id]["BANNED_WORDS"]:
            # per user
            cfg["THREATS"][user.id]["BANNED_WORDS"].add(word.lower())
            writeInfo()
            await ctx.send("{} Has been added to the blacklist for {}.".format(word.lower(), user.name))

@bot.command()
@commands.check(isOP)
async def removeBanWord(ctx, word):
    '''
    Remove a word from eithe the global or a particular blacklist.
    '''
    if len(ctx.message.mentions) == 0 and word.lower() in cfg["GLOBAL_BANNED_WORDS"]:
        # global
        cfg["GLOBAL_BANNED_WORDS"].remove(word.lower())
        writeInfo()
        await ctx.send("{} Has been removed from the global blacklist.".format(word.lower()))
    else:
        user = ctx.message.mentions[0]
        if user.id in cfg["THREATS"] and word.lower() in cfg["THREATS"][user.id]["BANNED_WORDS"]:
            # per user
            cfg["THREATS"][user.id]["BANNED_WORDS"].remove(word.lower())
            writeInfo()
            await ctx.send("{} Has been removed from the blacklist for {}.".format(word.lower(), user.name))

# maintainence methods
@bot.command()
@commands.check(isOP)
async def resetKick(ctx):
    '''
    Allows user to call genKick from bot.
    '''
    await genKick()
    await ctx.send("Kick Votes list has been successfully generated.")

@bot.command(name = "reloadVars")
@commands.check(isOP)
async def callreloadVars(ctx):
    '''
    Allows user to call reloadVars from bot.
    '''
    reloadVars()
    await ctx.send("Variables reloaded from file.")

@bot.command(name = "reloadVars")
@commands.check(isOwner)
async def shutdown(ctx):
    '''
    Shuts down the bot.
    '''
    await client.logout()
    await client.close()
    keep_alive.shutdown()
    
'''
Generalized list functions
Allows creation of **USER** collections on the fly with custom names
Will not work with other datatypes for now.
'''
def addToList(ListName, user, SUDO = False):
    '''
    Adds a user to a list of name ListName in the cfg file.
    Creates new list if it does not exist.
    '''
    if not ListName in cfg and (not ListName in PROTECTED_NAMES or SUDO):
        cfg[ListName] = [user.id]
    elif (not ListName in PROTECTED_NAMES or SUDO) and not user.id in cfg[ListName]:
        cfg[ListName].append(user.id)
    writeInfo()

def removeFromList(ListName, user, SUDO = False):
    '''
    Removes a user from a list of ListName in cfg if they are in it.
    '''
    if ListName in cfg and (not ListName in PROTECTED_NAMES or SUDO) and user in cfg[ListName]:
        cfg[ListName].remove(user.id)

        if len(cfg[ListName] == 0):
            # culling of empty lists.
            removeList(ListName)

        writeInfo()

def removeList(ListName, SUDO = False):
    '''
    Removes entire list.
    '''
    if ListName in cfg and (not ListName in PROTECTED_NAMES or SUDO):
        del cfg[ListName]
        writeInfo()

def getListUsers(ListName):
    '''
    Returns a list of users who are in the list of choice.
    '''
    try:
        if not ListName in PROTECTED_NAMES:
            return [client.get_guild(419214713252216848).get_member(i).name for i in cfg[ListName]]
    finally:
        return None

def getListUserNames(ListName):
    '''
    Creates a list of users' names in a given custom list.
    '''
    return [m.name for m in getListUsers(ListName)]

@bot.command()
@commands.check(isOP)
async def op(ctx):
    '''
    Opps a user
    '''
    user = ctx.message.mentions[0]
    addToList("OPS", user, SUDO=True)

@bot.command()
@commands.check(isOP)
async def deop(ctx):
    '''
    deops a user
    '''
    user = ctx.message.mentions[0]
    removeFromList("OPS", user, SUDO=True)

@bot.command()
@commands.check(isOP)
async def addKickSafe(ctx):
    '''
    Adds user to Kick Safe list.
    '''
    user = ctx.message.mentions[0]
    addToList("KICK_SAFE", user, SUDO=True)

@bot.command()
@commands.check(isOP)
async def removeKickSafe(ctx):
    '''
    Removes user from Kick Safe list.
    '''
    user = ctx.message.mentions[0]
    removeFromList("KICK_SAFE", user, SUDO=True)

# Custom list additions
@bot.command()
@commands.check(notThreat)
async def addCustomList(ctx, ListName):
    '''
    Adds a user to a custom list.
    '''
    addToList(ListName, ctx.message.mentions[0])
    await ctx.send("List \"{}\" consists of the following:{}".format(ListName, getListUserNames(ListName)))

@bot.command()
@commands.check(notThreat)
async def removeCustomList(ctx, ListName):
    '''
    Removes a user from a custom list.
    '''
    removeFromList(ListName, ctx.message.mentions[0])
    await ctx.send("List \"{}\" consists of the following:{}".format(ListName, getListUserNames(ListName)))

# *STATUS OF BOT TODO
@bot.command()
async def status(ctx):
    pass


# TODO Tomato function
@bot.command(name = u"\U0001F345")
async def tomato(ctx):
    pass




# Create webserver to keep bot running on Repl.it
keep_alive.keep_alive()
# Create loop task to perform timed actions
client.loop.create_task(dailyMSG())
# Finally, start the bot
client.run(TOKEN)

if __name__ == "__main__":
    cfg["LETHALITY"] = 1
    writeInfo()
