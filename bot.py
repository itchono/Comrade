# bot.py
import os
import dotenv
import discord

# text filtering
import re
import unidecode
from fuzzywuzzy import fuzz
from fuzzywuzzy import process


dotenv.load_dotenv()

TOKEN = os.environ.get('TOKEN')
GUILD = os.environ.get('GUILD')

print(TOKEN)
print(GUILD)

client = discord.Client()

kickList = {}

THREATS = ['Wahaha#0365', 'itchono#3597']

KICK_REQ = 3

def containsletters(string, check):
    res = True
    for i in range(len(check)-1):
        if string.find(check[i]) == -1 or string.find(check[i+1], string.find(check[i])) == -1:
            res = False
        
    return res
    
@client.event
async def on_message(message):
    if message.author != client.user:
        #failsafe against self response
        
        if (str(message.author) in THREATS):
            custom_emojis = re.findall(r'<:\w*:\d*>', message.content)
            print(custom_emojis)
            query = re.sub('\W+','', unidecode.unidecode(message.content.lower()))
            print(message.content)
            if 'hentai' in query or fuzz.partial_ratio('hentai', query) > 60:
                await message.delete()
                print('Message purged', str(message.content))
            
        
        if 'hello comrade' in message.content.lower():
            await message.channel.send('Henlo')
        if '$comrade' in message.content.lower():
            parse = str(message.content).strip('$comrade').split()
            print(parse)
            if parse[0] == 'voteKick':
                user = str(message.mentions[0].name)
            
                global kickList
                kickList[user] += 1
                await message.channel.send(str('Vote added. ' + str(KICK_REQ-kickList[user]) + ' more needed to kick.' ))
                if (kickList[user] >= KICK_REQ):
                    tgt = ''
                    for member in message.guild.members:
                        if str(member) == [parse[1]]:
                            tgt = member
                     
                    await message.channel.send(str('@' + str(tgt.name)+ ' has been kicked successfully'))

@client.event
async def on_message_edit(message1, message):  
    print('Edit detected')
    if message.author != client.user:
        #failsafe against self response
        
        if (str(message.author) in THREATS):
            
        
            query = re.sub('\W+','', unidecode.unidecode(message.content.lower()))
            if 'hentai' in query or fuzz.partial_ratio(query,'hentai') > 60:
                await message.delete()
                print('Message purged', str(message.content))
            

@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            global kickList
            # populate kicklist
            num_mem = 0
            for member in guild.members:
                num_mem +=1
                kickList[member.name] = 0
            print(num_mem, "members loaded.")
            break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})')
        
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Upholding Communism"))
    

client.run(TOKEN)