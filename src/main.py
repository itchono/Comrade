'''
Comrade Bot - Interim Branch

Developed for use while V3 is in development
Core modules:
- Wholesome buffer
- Absolute time stop

'''
# I: External Library Imports
import discord  # core to bot
from discord.ext import commands

# File reading for env vars
import os
import dotenv  # NOTE - install as "pip install python-dotenv"

# Misc stuff
from datetime import datetime, timedelta  # Time func

import asyncio  # Dependancy for Discord py

import random
import utilitymodules


t_start = datetime.utcnow()  # start time

# I: Variable Loading
dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN')  # bot token; kept private

VERSION = "Comrade v2.4 Legacy Version"

# Temporary Variables

wholesomebuffer = []

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
    await client.get_guild(419214713252216848).get_channel(707709158933266503).send(msg)

'''
COMMANDS
'''

async def STAR_PLATINUM(message, time, DIO=False):
    '''
    Stops time for (time + 2) seconds (includes windup animation)
    '''
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

@client.command()
async def timeStop(ctx, time):
    '''
    More potent version of time stop with variable lockdown timer
    '''
    await STAR_PLATINUM(ctx.message, time)

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
        if len(m.attachments) > 0: buffer.append(m.attachments[0].url)
    await log("Wholesome buffer of {} images.".format(len(buffer)))
    return buffer

@client.command()
async def reloadWholesome(ctx, name):
    global wholesomebuffer
    wholesomebuffer = await constructWBuffer()
    await ctx.send("Buffer reconstructed with {} images".format(len(wholesomebuffer)))

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

        # wholesome
        if message.content == ";td":
            n = random.randint(0, len(wholesomebuffer)-1)

            embed = discord.Embed()
            embed.set_image(url=wholesomebuffer[n])

            await message.channel.send(embed=embed)

        if message.mention_everyone or len(message.mentions) > 2: await message.add_reaction(await client.get_guild(419214713252216848).fetch_emoji(609216526666432534))
        # in the event that they mention lots of people
        
        await client.process_commands(message)  # interpret commands

@client.event
async def on_ready():
    global wholesomebuffer
    wholesomebuffer = await constructWBuffer()

    # Change presence accordingly
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Upholding Communism"))
    await log("Comrade is online. Starup completed in {}. Current UTC time is {}".format(datetime.utcnow() - t_start, datetime.utcnow()))

# Finally, start the bot
client.run(TOKEN)