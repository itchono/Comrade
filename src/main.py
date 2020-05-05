'''
Comrade Bot - V3.0 Tritium

More versatile and Adaptable Version of Comrade, Rewritten from the ground up
Mingde Yin

April - May 2020

'''
import os
import dotenv

import asyncio

import discord # core to bot
from discord.ext import commands

from AuxilliaryListener import *
from Commands import *
from MessageHandler import *


'''
VARIABLES

'''

print("Comrade V3 Starting...")

# private variable loading
dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN') # bot token; kept private

print("Variable Loading Complete")

from MongoInterface import *

client = commands.Bot(command_prefix="$c ", case_insensitive=True) # declare bot with prefix $c
client.add_cog(AuxilliaryListener(client))
client.add_cog(MessageHandler(client))
client.add_cog(Commands(client))


@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Testing Communism"))
    print("Bot is online")


client.run(TOKEN)






