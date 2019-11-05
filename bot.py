# bot.py
import os
import dotenv
import discord

# text filtering
import re
import unidecode
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# download pfps
import requests

dotenv.load_dotenv()

print('COMRADE BOT INITIALIZING...')

TOKEN = os.environ.get('TOKEN')
GUILD = os.environ.get('GUILD')

client = discord.Client()

print('Initializing parameters')

kickList = {}

kickVotes = {}

LETHALITY = 0

THREATS = ['Wahaha#0365', 'itchono#3597']

OPS = ['itchono#3597', 'Vyre#6300']

KICK_SAFE = ['itchono#3597', 'Comrade#2988']

KICK_REQ = 6

def containsletters(string, check):
    res = True
    for i in range(len(check)-1):
        if string.find(check[i]) == -1 or string.find(check[i+1], string.find(check[i])) == -1:
            res = False
        
    return res
    
@client.event
async def on_message(message):
    global LETHALITY
    global THREATS
    global OPS
    global kickVotes
    global kicklist
    global KICK_REQ
    
    if message.author != client.user:
        #failsafe against self response
        
        if (str(message.author) in THREATS and LETHALITY >= 2):
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
            parse = str(message.content).lstrip('$comrade').split()
            print(parse)
            if parse[0] == 'voteKick':
                user = str(message.mentions[0].name) #name of user to be kicked
                
                if not (str(message.author) in kickVotes[user] or user in KICK_SAFE):
                    kickList[user] += 1
                    kickVotes[user].append(str(message.author))
                    await message.channel.send('Vote added. ' + str(int(KICK_REQ)-int(kickList[user])) + ' more needed to kick.')
                    if (kickList[user] >= KICK_REQ):
                        for member in message.guild.members:
                            if str(member.name) == user:
                                if LETHALITY >= 1:
                                    kickList[user] = 0
                                    await message.channel.send('@' + str(member.name)+ ' has been kicked successfully')
                                    await message.guild.kick(member)
                                else:
                                    await message.channel.send('Lethal mode has been disabled. Please enable it with $comrade lethal <level>')
                                             
                else:
                    await message.channel.send('You have already voted!')
                 
            elif parse[0] == 'lethal' and str(message.author) in OPS:
                LETHALITY = int(parse[1])
                if LETHALITY == 0:
                    await message.channel.send('Lethal mode has been deactivated.')
                else:
                    await message.channel.send('Lethality has been activated and set to {0}. This can cause destructive actions.'.format(LETHALITY))
            elif parse[0] == 'addThreat' and str(message.author) in OPS:
                user = str(message.mentions[0])
                THREATS.append(user)
                await message.channel.send('Threat Added.')
            elif parse[0] == 'removeThreat' and str(message.author) in OPS:
                user = str(message.mentions[0])
                if user in THREATS:
                    THREATS.remove(user)
                await message.channel.send('Threat Added.')
            
            
            elif parse[0] == 'op' and str(message.author) in OPS:
                user = str(message.mentions[0])
                OPS.append(user)
                await message.channel.send('OP Added.')
            elif parse[0] == 'deop' and str(message.author) in OPS:
                user = str(message.mentions[0])
                if user in OPS:
                    OPS.remove(user)
                await message.channel.send('OP Removed.')
                
            elif parse[0] == 'arrayStatus':
                kicks = []
                for member in message.guild.members:
                    if kickList[str(member.name)] >= 1:
                        kicks.append(str(member.name) + ': ' + str(kickList[str(member.name)]))
            
                await message.channel.send('Threats: ' + str(THREATS) + '\nOPS:' + str(OPS) + '\nKick Requirement: ' + str(KICK_REQ) + "\nKick List: " + str(kicks))
                
            elif parse[0] == 'kickReq' and str(message.author) in OPS:
                KICK_REQ = int(parse[1])
                await message.channel.send('Kick requirement has been set to {0} votes.'.format(KICK_REQ))
            elif parse[0] == 'resetKick' and str(message.author) in OPS:
                for member in message.guild.members:
                    kickList[member.name] = 0
                    kickVotes[member.name] = []
                await message.channel.send('Kore wa requiem: All kick votes have been reset.')
                
                
                
                    

@client.event
async def on_message_edit(message1, message):  
    print('Edit detected')
    if message.author != client.user:
        #failsafe against self response
        
        if (str(message.author) in THREATS and LETHALITY >= 2):
            query = re.sub('\W+','', unidecode.unidecode(message.content.lower()))
            if 'hentai' in query or fuzz.partial_ratio(query,'hentai') > 60:
                await message.delete()
                print('Message purged', str(message.content))
            

@client.event
async def on_ready():
    # file = open("avatarlinks.txt", "w")
    
    print('Constructing member list')

    for guild in client.guilds:
        if guild.name == GUILD:
            global kickList
            # populate kicklist
            num_mem = 0
            for member in guild.members:
                num_mem +=1
                kickList[member.name] = 0
                kickVotes[member.name] = []
                
                
                '''
                url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(member)
                
                r = requests.get(url)
                with open('C:/Users/mdsup/Documents/GitHub/Comrade/avatars/avatar{0}.png'.format(member.id), 'wb') as outfile:
                    outfile.write(r.content)
                
                file.write(url + '\n')
                '''
                
            print(num_mem, "members loaded.")
            break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})')
        
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Upholding Communism"))
    # file.close()

    print('COMRADE is fully online.')

client.run(TOKEN)