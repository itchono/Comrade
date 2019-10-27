# bot.py
import os

import discord
f = list(open('.env'))

TOKEN = f[0].strip('\n')
GUILD = f[1].strip('\n')

print(TOKEN)
print(GUILD)

client = discord.Client()

@client.event
async def on_message(message):
    if message.author != client.user:
        #failsafe against self response
        print(str(message.author))
        if (str(message.author) == 'Wahaha#0365'):
            await message.channel.send('ur bad lol')
        print(message.content.lower())
        if 'hello comrade' in message.content.lower():
            await message.channel.send('Henlo')
            

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})')
    
    

client.run(TOKEN)