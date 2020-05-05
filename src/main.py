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


'''
VARIABLES

'''

print("Comrade V3 Starting...")
dotenv.load_dotenv()
TOKEN = os.environ.get('TOKEN') # bot token; kept private
client = commands.Bot(command_prefix="$c ") # declare bot with prefix $c

@client.command
async def memeapproved(ctx):
    await ctx.send("Meme Approved")

@client.event
async def on_message(message:discord.message):
    if message.author != client.user:
        if "hello" in message.content.lower():
            msg = await message.channel.send("Henlo")
            await asyncio.sleep(5)
            await msg.delete()

print("Bot is online")
client.run(TOKEN)





