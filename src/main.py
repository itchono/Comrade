'''
Comrade Bot - Interim Branch

Developed for use while V3 is in development
Core modules:
- Daily announcement
- Moderation

'''

# I: External Library Imports
import discord  # core to bot
from discord.ext import commands

# Text Filtering
import re
import unidecode
# ALSO: need python-levenshtein ==> needs C++ build tools installed
from fuzzywuzzy import fuzz

# File reading for env vars
import os
import dotenv  # NOTE - install as "pip install python-dotenv"

# Misc stuff
from datetime import datetime, timedelta  # Time func

import asyncio  # Dependancy for Discord py

import random
from importlib import reload

# II: Internal Imports
import keep_alive
import utilitymodules

'''
Handy Stuff

client.get_guild(419214713252216848) is my server.

'''

'''
Initialization Phase

- Load env variables
- Declare client
- Load internal variables from DB

'''
print('Comrade is currently starting up...')
t_start = datetime.utcnow()  # start time

# I: Variable Loading
dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN')  # bot token; kept private

try:
    from data import comrade_cfg
    cfg = comrade_cfg.data  # load config variables
except:
    cfg = {}

PROTECTED_NAMES = ["LETHALITY", "THREATS", "kickVotes", "OPS",
                   "GLOBAL_BANNED_WORDS", "PURGE", "LAST_DAILY", "KICK_REQ", "KICK_SAFE", "ANTIPING"]
# Protected dictionary elements in cfg file
WHITELISTED_CHANNELS = [558408620476203021,
                        522428899184082945]  # TODO Command-ify
# exempt from filter

VERSION = "Comrade v2.3 Interim Patch"

# Temporary Variables
infractions = {}

wholesomebuffer = []

print('All variables loaded.')

# II: Client startup PT 1
# declare bot with prefix $comrade
client = commands.Bot(command_prefix="$comrade ")

'''
FUNCTIONS
'''


async def log(msg):
    '''
    Logs stuff into preferred log channel and keeps server-side log.
    '''
    await client.get_guild(419214713252216848).get_channel(446457522862161920).send(msg)
    with open("log.txt", "a") as f:
        f.write("{0} UTC: {1}\n".format(datetime.utcnow(), msg))


async def writeInfo():
    '''
    Writes changes made to cfg dictionary to configuration file.
    '''
    if os.path.exists("data/comrade_cfg.py"):
        os.remove("data/comrade_cfg.py")
        with open("data/comrade_cfg.py", "w") as f:
            f.write("{} = {}\n".format("data", cfg))
        await reloadVars()
        # announce to log channel
        await log("Data Written Successfully.")
    else:
        await log("Data could not be written.")

async def reloadVars():
    '''
    Reloads variables from configuration file dynamically if needed
    '''
    global cfg
    reload(comrade_cfg)
    cfg = comrade_cfg.data
    await log("Variables Successfully Reloaded From File.")


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
        yesterday = datetime.now()-timedelta(hours=1)
        async for msg in channel.history(limit=None, after=yesterday):
            if msg.author == client.user:
                try:
                    await msg.delete()
                except:
                    await log("Some messages could not be deleted.")


async def dailyRole():
    '''
    Sets new daily member, removing all previous daily member roles
    '''
    members = list(filter(lambda member: (not member.bot),
                          client.get_guild(419214713252216848).members))
    random.seed()  # important to seed random user
    chosenone = random.randint(0, len(members)-1)

    s = members[chosenone].name

    for member in client.get_guild(419214713252216848).members:
        currRoles = member.roles
        for r in currRoles:
            if r.id == 655670092679479296:  # Daily
                currRoles.remove(r)
                await member.edit(roles=currRoles)
                # remove the role if Daily'd
        if member == members[chosenone]:
            currRoles.append(client.get_guild(
                419214713252216848).get_role(655670092679479296))
            await member.edit(roles=currRoles)
            await client.get_guild(419214713252216848).get_channel(419214713755402262).send('Today\'s daily member is {}'.format(s))


async def dailyMSG(force=False):
    '''
    Daily routine at 7 AM EST. Used to make announcement and some others.
    Can be force called.
    '''
    await client.wait_until_ready()

    while not client.is_closed():
        if (datetime.utcnow().date() > lastDaily().date() and datetime.utcnow().hour == 12 and datetime.utcnow().minute <= 5) or force:
            cfg["LAST_DAILY"] = str(datetime.utcnow().date())
            await writeInfo()
            await log("Daily Announcement Made. Current LAST_DAILY = {}".format(cfg["LAST_DAILY"]))
            # make announcement
            await dailyRole()  # do daily role
        await asyncio.sleep(60)


async def genKick():
    '''
    Generates/Regenerates kicklist for all members on server
    '''
    cfg["kickVotes"] = {}  # refresh

    for member in client.get_guild(419214713252216848).members:
        cfg["kickVotes"][member.id] = []

    await writeInfo()
    await log("Kicklist regenerated - {} members loaded.".format(len(cfg["kickVotes"])))


async def quarantine(user: discord.user):
    '''
    (user object)

    Quarantines or unquarantines a user.
    '''
    currRoles = user.roles
    isQ = False
    for r in currRoles:
        if r.id == 613106246874038274:  # quarantine role
            isQ = True
            currRoles.remove(r)
            # remove the role if quarantined
        elif r.id == 419215295232868361:  # regular role
            currRoles.remove(r)
    if isQ:
        currRoles.append(client.get_guild(
            419214713252216848).get_role(419215295232868361))
        await log("User Released: {}".format(user.name))
        await user.edit(roles=currRoles)
        return '{} has been returned to society.'.format(user.name)
    else:
        currRoles.append(client.get_guild(
            419214713252216848).get_role(613106246874038274))
        await log("User Quarantined: {}".format(user.name))
        await user.edit(roles=currRoles)
        return '{} has been quarantined.'.format(user.name)


async def sentinelFilter(message: discord.message):
    '''
    Sentinel message filtering system, allows for multivalent toggles
    '''
    THRESHOLD = 70

    if not message.channel.id in WHITELISTED_CHANNELS:
        # Stage 1: text detection
        # clean message content down to text
        query = re.sub("\W+", '', unidecode.unidecode(message.content.lower()))

        # 3 Stages of filtering: 1) Emoji pass through 2) Eliminating nonstandard unicode chars 3) Regex Substitutions to eliminate non word characters

        # determines whether message filtering should be relaxed (needs exact content) or strict (75% match)
        strict = (message.author.id in cfg["THREATS"] and cfg["THREATS"]
                  [message.author.id]["LETHALITY"] >= 3) or cfg["LETHALITY"] >= 3
        superStrict = (message.author.id in cfg["THREATS"] and cfg["THREATS"][message.author.id]
                       ["LETHALITY"] >= 4) or cfg["LETHALITY"] >= 3  # even more strict filtering when needed

        for word in set(cfg["GLOBAL_BANNED_WORDS"]).union(set(cfg["THREATS"][message.author.id]["BANNED_WORDS"] if message.author.id in cfg["THREATS"] else set())):
            # checks every banned word for that user
            if (word in query or (len(query) > 2 and strict and fuzz.partial_ratio(word, query) > THRESHOLD)) or (word in utilitymodules.emojiToText(message.content.lower()) or (strict and fuzz.partial_ratio(word, utilitymodules.emojiToText(message.content.lower())) > THRESHOLD)):
                # passes query through fuzzy filtering system IF length of word is long enough and author is subhect to strict filtering
                await message.delete()
                await log('Message purged for bad word:\n' + str(message.content) + "\nSent By " + str(message.author.name) + "\nTrigger:" + str(word) + "\nMatch %:" + str(max([fuzz.partial_ratio(word, query), fuzz.partial_ratio(word, utilitymodules.emojiToText(message.content.lower()))])))
                await infraction(message, message.author, int(cfg["THREATS"][message.author.id]["LETHALITY"]/4))

        # Stage 2: Attachment Filtering
        if strict and (len(message.attachments) > 0 or len(message.embeds) > 0):
            await message.delete()
            await log('Message purged for embed; sent by ' + str(message.author.name))
            await infraction(message, message.author, int(cfg["THREATS"][message.author.id]["LETHALITY"]/4)*2)

        # Stage 3: Ping Filtering
        if superStrict and len(message.mentions) > 0:
            await message.delete()
            await message.channel.send("USELESS PING DETECTED SENT BY {}".format(message.author.mention))
            await infraction(message, message.author, int(cfg["THREATS"][message.author.id]["LETHALITY"]/4)*4)


async def infraction(msg, user, weight):
    '''
    Social credit-esque score used to punish users.
    '''
    LIMIT = 10

    if (weight > 0):
        if not user.id in infractions:
            infractions[user.id] = weight
        else:
            infractions[user.id] += weight
        m = await msg.channel.send("{3} demerit points added to {0}. ({1}/{2})".format(user.mention, infractions[user.id], LIMIT, weight))
        await log("{3} demerit points added to {0}. ({1}/{2})".format(user.mention, infractions[user.id], LIMIT, weight))
        await asyncio.sleep(10)
        await m.delete()

        if infractions[user.id] >= LIMIT:
            await msg.channel.send("Kicking {}...".format(user.name))
            await msg.guild.kick(user)

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
    cfg["kickVotes"][user.id].append(ctx.author.id)  # Add vote
    num_votes = len(cfg["kickVotes"][user.id])
    await writeInfo()
    await ctx.send("Vote added for {0} ({1}/{2}).".format(user.name, num_votes, cfg["KICK_REQ"]))

    # Check if threshold is met
    if num_votes >= cfg["KICK_REQ"]:
        if cfg["LETHALITY"] >= 1:
            await ctx.send("Kicking {}...".format(user.name))
            await ctx.guild.kick(user)
            genKick()  # regen list
        else:
            await ctx.send("Kicking has been disabled. Lethality must be at least 1 to continue (current = {}).".format(cfg["LETHALITY"]))

# Kick System
@client.command()
@commands.check(notThreat)
async def voteKick(ctx):
    '''
    Checks to see whether to add vote to kick a user.
    '''
    user = ctx.message.mentions[0]
    if ctx.author.id in cfg["kickVotes"][user.id]:
        await ctx.send("You have already voted!")
    elif user.id in cfg["KICK_SAFE"]:
        await ctx.send("Target is in Kick Safe list!")
    elif ctx.author.id in cfg["THREATS"] and cfg["THREATS"][ctx.author.id]["LETHALITY"] >= 1:
        await ctx.send("Due to you being a threat, you are not allowed to vote!")
    else:
        await addKick(ctx, user)


@client.command()
@commands.check(notThreat)
async def unKick(ctx):
    '''
    Removes vote from user.
    '''
    user = ctx.message.mentions[0]
    if ctx.author.id in cfg["kickVotes"][user.id]:
        cfg["kickVotes"][user.id].remove(ctx.author.id)
        num_votes = len(cfg["kickVotes"][user.id])
        await writeInfo()
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
@client.command(name="lethal")
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
            await writeInfo()
            await ctx.send("Global Lethality has been set to {}.".format(cfg["LETHALITY"]))
        # Modificaiton for a single user (in THREATS)
        else:
            user = ctx.message.mentions[0]
            if user.id in cfg["THREATS"]:
                cfg["THREATS"][user.id]["LETHALITY"] = float(Lnew)
                await writeInfo()
                await ctx.send("User Lethality has been set to {}.\nPlease ensure global lethality is set accordingly to enable lethal features.".format(cfg["THREATS"][user.id]["LETHALITY"]))
    else:
        await ctx.send("Invalid Input.")


@client.command(name="kickReq")
@commands.check(isOP)
async def setKickReq(ctx, Knew):
    if int(Knew) >= 1:
        cfg["KICK_REQ"] = int(Knew)
        await writeInfo()
        await ctx.send("Kick Requirement Set to {} votes.".format(cfg["KICK_REQ"]))
    else:
        await ctx.send("Invalid input.")


@client.command(name="quarantine")
@commands.check(isOP)
async def callQuarantine(ctx):
    '''
    Quarantines mentioned user
    '''
    user = ctx.message.mentions[0]
    await ctx.send(await quarantine(user))

@client.command()
@commands.check(isOP)
async def timeStop(ctx, time):
    '''
    More potent version of time stop with variable lockdown timer
    '''
    await STAR_PLATINUM(ctx.message, time)

# Threat dictionary methods
@client.command()
@commands.check(isOP)
async def addThreat(ctx, *args):
    '''
    Adds user to threats list with or without a preset lethality level (default: 3)
    '''
    level = int(args[0]) if len(
        args) > 0 else 3  # ternary assignment to use as default parameter
    user = ctx.message.mentions[0]
    if not user.id in cfg["THREATS"]:
        cfg["THREATS"][user.id] = {"LETHALITY": level, "BANNED_WORDS": set()}
        await writeInfo()
        await ctx.send("Threat Added with Lethality = {}".format(cfg["THREATS"][user.id]["LETHALITY"]))


@client.command()
@commands.check(isOP)
async def removeThreat(ctx):
    '''
    Removes target user from threats list.
    '''
    user = ctx.message.mentions[0]
    if user.id in cfg["THREATS"]:
        del cfg["THREATS"][user.id]
        await writeInfo()
        await ctx.send("Threat removed.")


@client.command()
@commands.check(isOP)
async def addBanWord(ctx, word):
    '''
    Adds a banned word, either to the global set or to a particular user.
    Use "" Quotes to enclose larger phrases
    '''
    if len(ctx.message.mentions) == 0 and not word.lower() in cfg["GLOBAL_BANNED_WORDS"]:
        # global
        cfg["GLOBAL_BANNED_WORDS"].add(word.lower())
        await writeInfo()
        await ctx.send("{} Has been added to the global blacklist.".format(word.lower()))
    else:
        user = ctx.message.mentions[0]
        if user.id in cfg["THREATS"] and not word.lower() in cfg["THREATS"][user.id]["BANNED_WORDS"]:
            # per user
            cfg["THREATS"][user.id]["BANNED_WORDS"].add(word.lower())
            await writeInfo()
            await ctx.send("{} Has been added to the blacklist for {}.".format(word.lower(), user.name))


@client.command()
@commands.check(isOP)
async def removeBanWord(ctx, word):
    '''
    Remove a word from eithe the global or a particular blacklist.
    '''
    if len(ctx.message.mentions) == 0 and word.lower() in cfg["GLOBAL_BANNED_WORDS"]:
        # global
        cfg["GLOBAL_BANNED_WORDS"].remove(word.lower())
        await writeInfo()
        await ctx.send("{} Has been removed from the global blacklist.".format(word.lower()))
    else:
        user = ctx.message.mentions[0]
        if user.id in cfg["THREATS"] and word.lower() in cfg["THREATS"][user.id]["BANNED_WORDS"]:
            # per user
            cfg["THREATS"][user.id]["BANNED_WORDS"].remove(word.lower())
            await writeInfo()
            await ctx.send("{} Has been removed from the blacklist for {}.".format(word.lower(), user.name))

# Maintainence methods
@client.command()
@commands.check(isOP)
async def resetKick(ctx):
    '''
    Allows user to call genKick from bot.
    '''
    await genKick()
    await ctx.send("Kick Votes list has been successfully generated.")


@client.command()
@commands.check(isOP)
async def resetInfractions(ctx):
    '''
    Resets demerit points
    '''
    global infractions
    infractions = {}


@client.command(name="reloadVars")
@commands.check(isOP)
async def callreloadVars(ctx):
    '''
    Allows user to call reloadVars from bot.
    '''
    await reloadVars()
    await ctx.send("Variables reloaded from file.")

'''
Generalized list functions
Allows creation of **USER** collections on the fly with custom names
Will not work with other datatypes for now.
'''

async def addToList(ListName, user, SUDO=False):
    '''
    Adds a user to a list of name ListName in the cfg file.
    Creates new list if it does not exist.
    '''
    if not ListName in cfg and (not ListName in PROTECTED_NAMES or SUDO):
        cfg[ListName] = [user.id]
    elif (not ListName in PROTECTED_NAMES or SUDO) and not user.id in cfg[ListName]:
        cfg[ListName].append(user.id)
    await writeInfo()


async def removeFromList(ListName, user, SUDO=False):
    '''
    Removes a user from a list of ListName in cfg if they are in it.
    '''
    if ListName in cfg and (not ListName in PROTECTED_NAMES or SUDO) and user.id in cfg[ListName]:
        cfg[ListName].remove(user.id)

        if len(cfg[ListName]) == 0:
            # culling of empty lists.
            removeList(ListName)

        await writeInfo()


async def removeList(ListName, SUDO=False):
    '''
    Removes entire list.
    '''
    if ListName in cfg and (not ListName in PROTECTED_NAMES or SUDO):
        del cfg[ListName]
        await writeInfo()


def getListUsers(ListName, SUDO=False):
    '''
    Returns a list of users who are in the list of choice.
    '''
    try:
        if not ListName in PROTECTED_NAMES or SUDO:
            return [client.get_guild(419214713252216848).get_member(i) for i in cfg[ListName]]
    except:
        return None


def getListUserNames(ListName):
    '''
    Creates a list of users' names in a given custom list.
    '''
    return [m.name for m in getListUsers(ListName)]


@client.command()
@commands.check(isOP)
async def op(ctx):
    '''
    Opps a user
    '''
    user = ctx.message.mentions[0]
    await addToList("OPS", user, SUDO=True)


@client.command()
@commands.check(isOP)
async def deop(ctx):
    '''
    deops a user
    '''
    user = ctx.message.mentions[0]
    await removeFromList("OPS", user, SUDO=True)


@client.command()
@commands.check(isOP)
async def addKickSafe(ctx):
    '''
    Adds user to Kick Safe list.
    '''
    user = ctx.message.mentions[0]
    await addToList("KICK_SAFE", user, SUDO=True)


@client.command()
@commands.check(isOP)
async def removeKickSafe(ctx):
    '''
    Removes user from Kick Safe list.
    '''
    user = ctx.message.mentions[0]
    await removeFromList("KICK_SAFE", user, SUDO=True)


@client.command()
@commands.check(isOP)
async def antiping(ctx):
    '''
    Prevents user from pinging
    '''
    user = ctx.message.mentions[0]
    if user in getListUsers("ANTIPING", SUDO=True):
        await removeFromList("ANTIPING", user, SUDO=True)
    else:
        await addToList("ANTIPING", user, SUDO=True)

# Custom list additions
@client.command()
async def helpList(ctx):
    '''
    Shows help for lists
    '''
    await ctx.send("```CUSTOM LISTS:\n- Show lists using $comrade showLists\n- Add a member to a new OR existing list using $comrade addList <List Name> <@mention>\n- Remove a member from a list using $comrade removeList <List Name> <@mention>\n- Check list members using $comrade checkList <List Name>\n- See this info again using $comrade helpList```")


@client.command()
@commands.check(notThreat)
async def showLists(ctx):
    '''
    Lists the custom lists.
    '''
    names = ''
    for s in cfg:
        if not s in PROTECTED_NAMES:
            names += s + '\n'
    if names == '':
        names = 'None'
    await ctx.send("```Custom Lists:\n" + names + "```")


@client.command()
@commands.check(notThreat)
async def addList(ctx, ListName):
    '''
    Adds a user to a custom list.
    '''
    await addToList(ListName, ctx.message.mentions[0])
    await ctx.send("List \"{}\" consists of the following:{}".format(ListName, getListUserNames(ListName)))


@client.command(name="removeList")
@commands.check(notThreat)
async def removeFList(ctx, ListName):
    '''
    Removes a user from a custom list.
    '''
    await removeFromList(ListName, ctx.message.mentions[0])
    await ctx.send("Removal Successful.")


@client.command()
async def checkList(ctx, ListName):
    '''
    Shows members of list
    '''
    if ListName in cfg and not ListName in PROTECTED_NAMES:
        await ctx.send("List \"{}\" consists of the following:{}".format(ListName, getListUserNames(ListName)))
    else:
        await ctx.send("That list does not exist!")

# Bot cleaning
@client.command()
async def clear(ctx):
    '''
    Clears all messages, callable from bot.
    '''
    await cleanMSG()
    await ctx.message.delete()

# *STATUS OF BOT TODO
@client.command()
@commands.check(notThreat)
async def status(ctx, *args):
    '''
    Reports the bot's status.
    Comes in two flavours; full and basic (default)
    '''
    kickList = [(str(ctx.guild.get_member(i)) + ": " + str(len(cfg["kickVotes"][i])))
                for i in cfg["kickVotes"] if len(cfg["kickVotes"][i]) > 0]
    OPS = [str(ctx.guild.get_member(i)) for i in cfg["OPS"]]
    THREATS = [(str(ctx.guild.get_member(i)) + " - Lethality = " + str(cfg["THREATS"][i]["LETHALITY"]) +
                " - Banned Words:" + str(cfg["THREATS"][i]["BANNED_WORDS"]) + "\n") for i in cfg["THREATS"]]
    LETHALITY = cfg["LETHALITY"]
    KICK_REQ = cfg["KICK_REQ"]
    KICK_SAFE = [str(ctx.guild.get_member(i)) for i in cfg["KICK_SAFE"]]
    GLOBAL_WDS = str(cfg["GLOBAL_BANNED_WORDS"])

    uptime = datetime.utcnow() - t_start
    if len(args) > 0 and args[0] == "full":
        msg = await ctx.send("```Uptime: {0}\nGlobal Lethality: {1}\nKick Votes: {2}\nKick Requirement: {3}\nOPS: {4}\nThreats: {5}\nKick Safe: {6}\n Global Banned Words: {7}```".format(uptime, LETHALITY, kickList, KICK_REQ, OPS, THREATS, KICK_SAFE, GLOBAL_WDS))
        await asyncio.sleep(10)
        await msg.delete()
    else:
        msg = await ctx.send("```Uptime: {0}\nGlobal Lethality: {1}\nKick Votes: {2}\nKick Requirement: {3}```".format(uptime, LETHALITY, kickList, KICK_REQ))
        await asyncio.sleep(10)
        await msg.delete()


@client.command()
async def lethalityhelp(ctx):
    '''
    Gives a quick guide on lethality.
    '''
    await ctx.send("LETHALITY SYSTEM\nWorks under 2 regimes - Global and Per User.\nGlobal: Enables and disables features at various levels\n0: None\n1: Kicking enabled\n2: Message Filtering for threats enabled\n3: Message filtering for all users enabled\n4: Purge enabled\n\nPer user: Subjects users in THREATS list to stricter conditions; subject to limitation by global lethality\n0: No restrictions\n1: No voting of any form\n2: Messages filtered (relaxed)\n3: Messages filtered strictly\n4: Loss of ability to ping")

# Fun stuff
@client.command()
@commands.check(notThreat)
async def textToEmoji(ctx, s):
    '''
    Uses the emoji converter in utilities to convert a string of text to emoji.
    '''
    await ctx.send(utilitymodules.textToEmoji(s))


@client.command()
@commands.check(notThreat)
async def emojiToText(ctx, s):
    '''
    Uses the emoji converter in utilities to convert some emojis to plaintext.
    '''
    await ctx.send(utilitymodules.emojiToText(s))


@client.command()
async def version(ctx):
    '''
    Indicates version
    '''
    await ctx.send("Comrade is currently running on version: {}".format(VERSION))


@client.command()
async def wholesome(ctx):
    '''
    Sends a random image from the wholesome channel.
    '''

    n = random.randint(0, len(wholesomebuffer)-1)

    embed = discord.Embed()
    embed.set_image(url=wholesomebuffer[n])

    await ctx.send(embed=embed)


async def constructWBuffer():
    '''
    builds buffer of wholesome images
    '''

    buffer = []

    async for m in client.get_guild(419214713252216848).get_channel(642923261977559061).history(limit=None):
        if len(m.attachments) > 0:
            buffer.append(m.attachments[0].url)

    await log("Wholesome buffer of {} images.".format(len(buffer)))

    return buffer



@client.command()
@commands.check(isOP)
async def reloadWholesome(ctx, name):
    global wholesomebuffer
    wholesomebuffer = await constructWBuffer()
    await ctx.send("Buffer reconstructed with {} images".format(len(wholesomebuffer)))


'''
MESSAGE EVENTS
'''

# TODO these need some work (user is able to speak)


async def STAR_PLATINUM(message, time, DIO=False):
    '''
    Stops time for (time + 2) seconds (includes windup animation)
    '''

    if not message.author.id in cfg["THREATS"] or cfg["THREATS"][message.author.id]["LETHALITY"] == 0:
        embed = discord.Embed(
            title=("ZA WARUDO" if not DIO else "TOKI WO TOMARE"),
            colour=discord.Colour.from_rgb(r=102, g=0, b=204)

        )
        embed.set_image(url=(
            "https://media1.tenor.com/images/4b953bf5b5ba531099a823944a5626c2/tenor.gif" if not DIO else "https://media1.tenor.com/images/afc87b53146aaeaf78eaad0bb50fd8a2/tenor.gif"))

        m1 = await message.channel.send(embed=embed)
        # Remove ability for people to talk and TODO: allow daily member to talk
        await message.channel.set_permissions(message.guild.get_role(419215295232868361), send_messages=False)
        await message.channel.set_permissions(message.guild.get_role(675888063192236067), send_messages=False)

        await asyncio.sleep((1.95 if not DIO else 1.65))
        await m1.delete()

        mt = await message.channel.send("*Time is frozen*")

        # fun counter thing
        if int(time) <= 20:
            for i in range(int(time)):
                await asyncio.sleep(1)

                t = i+1
                if t == 1:
                    await mt.edit(content="1 second has passed", suppress=False)
                else:
                    await mt.edit(content="{} seconds have passed".format(t), suppress=False)

        else:
            await asyncio.sleep(int(time)-2 if int(time) >= 2 else 0)

        await message.channel.set_permissions(message.guild.get_role(419215295232868361), send_messages=True)
        await message.channel.set_permissions(message.guild.get_role(675888063192236067), send_messages=True)

        embed = discord.Embed(
            title="Time has begun to move again.",
            colour=discord.Colour.from_rgb(r=102, g=0, b=204)
        )
        embed.set_image(url=(
            "https://media1.tenor.com/images/02c68c840e943c4aa2ebfdb7c8a6ea46/tenor.gif" if not DIO else "https://media1.tenor.com/images/70e9c6a725051566e1bd6ce79e34d136/tenor.gif"))

        m2 = await message.channel.send(embed=embed)

        await asyncio.sleep(1.35)
        await m2.delete()
        await mt.edit(content="*Time has begun to move again.*", suppress=False)

        await log("Time stop of duration {}".format(time))
    else:

        m2 = await message.channel.send("You are unworthy to use the power of a stand!")

        await asyncio.sleep(5)
        await m2.delete()

purge_tgt = None

def is_user(m):
    return m.author == purge_tgt

@client.event
async def on_message(message: discord.message):
    '''
    Triggers whenever a message is sent anywhere visible to the bot.
    '''
    if message.author != client.user:
        # Check to prevent feedback loop

        # Filter messages
        if cfg["LETHALITY"] >= 4 or (cfg["LETHALITY"] >= 2 and message.author.id in cfg["THREATS"] and cfg["THREATS"][message.author.id]["LETHALITY"] >= 2):
            await sentinelFilter(message)

        # Greeting function (one of the earliest functions that Comrade had)
        if 'hello comrade' in message.content.lower():
            await message.channel.send('Henlo')
        elif 'henlo comrade' in message.content.lower():
            await message.channel.send('Hello')
        elif 'comrade' in message.content.lower() and fuzz.partial_ratio('hello', message.content.lower()) > 50 and not '$' in message.content.lower():
            await message.channel.send('Good day!')

        # fun stuff
        if message.content == "STAR PLATINUM":
            await STAR_PLATINUM(message, 5)
        elif message.content == "ZA WARUDO":
            await STAR_PLATINUM(message, 10, DIO=True)

        # wholesome
        if message.content == ";td":
            n = random.randint(0, len(wholesomebuffer)-1)

            embed = discord.Embed()
            embed.set_image(url=wholesomebuffer[n])

            await message.channel.send(embed=embed)

        if message.mention_everyone or len(message.mentions) > 2:
            # react to @everyone
            await message.add_reaction(await client.get_guild(419214713252216848).fetch_emoji(609216526666432534))
            668273444684693516

        if message.author in getListUsers("ANTIPING", SUDO=True) and len(message.mentions) > 0:
            # react, specifically to raf
            l = message.content

            await message.delete()

            m = await message.channel.send("Message deleted due to useless ping mentioning {}".format(message.mentions[0].name))

            await message.channel.send("```" + l + "```")

            await asyncio.sleep(5)

            await m.delete()

        await client.process_commands(message)  # interpret commands


@client.event
async def on_message_edit(OG: discord.message, message: discord.message):
    '''
    Triggers when message is edited.
    '''
    # Filter message
    if cfg["LETHALITY"] >= 4 or (cfg["LETHALITY"] >= 2 and message.author.id in cfg["THREATS"] and cfg["THREATS"][message.author.id]["LETHALITY"] >= 2):
        await sentinelFilter(message)

'''
CLIENT INIT Cont'
'''
@client.event
async def on_ready():
    for guild in client.guilds:
        # detect home guild
        if guild.id == 419214713252216848:
            print("Connected successfully to {} (id = {})".format(
                guild.name, guild.id))

            if len(cfg["kickVotes"]) != len(guild.members):
                # regenerate kickList if number of members has changed
                await genKick()
                print(
                    "ATTN: kickVotes was updated due to a change in the number of members")
            print("{} members detected.".format(len(guild.members)))

    global wholesomebuffer

    wholesomebuffer = await constructWBuffer()

    print("{} is online and ready to go.".format(client.user))

    # Change presence accordingly
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Upholding Communism"))
    await client.get_guild(419214713252216848).get_channel(446457522862161920).send("Comrade is online. Current UTC time is {}".format(datetime.utcnow()))

    # DONE
    print("Done! Time taken: {}".format(datetime.utcnow() - t_start))

# Client startup PT 2
print('Starting Internal Server...')
# Create webserver to keep bot running on Repl.it
#keep_alive.keep_alive()
# Create loop task to perform timed actions
client.loop.create_task(dailyMSG())
# Finally, start the bot
client.run(TOKEN)

# END OF FILE
