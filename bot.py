# bot.py
import os
import dotenv
import discord


dotenv.load_dotenv()

TOKEN = os.environ.get('TOKEN')
GUILD = os.environ.get('GUILD')

print(TOKEN)
print(GUILD)

client = discord.Client()

kickList = {}

KICK_REQ = 3
    
@client.event
async def on_message(message):
    if message.author != client.user:
        #failsafe against self response
        print(str(message.author))
        if (str(message.author) == 'Wahaha#0365'):
            await message.channel.send('ur bad lol')
        if 'hello comrade' in message.content.lower():
            await message.channel.send('Henlo')
        if '$comrade' in message.content.lower():
            parse = str(message.content).strip('$comrade').split()
            print(parse)
            if parse[0] == 'voteKick':
                global kickList
                kickList[parse[1]] += 1
                await message.channel.send(str('Vote added. ' + str(KICK_REQ-kickList[parse[1]]) + ' more needed to kick.' ))
                if (kickList[parse[1]] >= KICK_REQ):
                    tgt = ''
                    for member in message.guild.members:
                        if str(member) == [parse[1]]:
                            tgt = member
                     
                    await message.channel.send(str('@' + str(tgt)+ ' has been kicked successfully'))
            
            

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break
    kzCounter = 0
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})')
    

client.run(TOKEN)