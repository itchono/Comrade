'''
Comrade Bot - Interim Branch

Developed for use while V3 is in development
Core modules:
- User lists

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

VERSION = "Comrade v2.3.1 Interim Patch 3"

# Temporary Variables

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


@client.command()
@commands.check(isOP)
async def timeStop(ctx, time):
    '''
    More potent version of time stop with variable lockdown timer
    '''
    await STAR_PLATINUM(ctx.message, time)


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

    await ctx.send("```Uptime: {0}\nGlobal Lethality: {1}\nKick Votes: {2}\nKick Requirement: {3}```".format(uptime, LETHALITY, kickList, KICK_REQ))


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
        # Greeting function (one of the earliest functions that Comrade had)
        if 'hello comrade' in message.content.lower():
            await message.channel.send('Henlo')
        elif 'henlo comrade' in message.content.lower():
            await message.channel.send('Hello')

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

        await client.process_commands(message)  # interpret commands

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

    global wholesomebuffer

    wholesomebuffer = await constructWBuffer()

    print("{} is online and ready to go.".format(client.user))

    # Change presence accordingly
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Upholding Communism"))
    await client.get_guild(419214713252216848).get_channel(446457522862161920).send("Comrade is online. Current UTC time is {}".format(datetime.utcnow()))

    # DONE
    print("Done! Time taken: {}".format(datetime.utcnow() - t_start))

# Finally, start the bot
client.run(TOKEN)

# END OF FILE
