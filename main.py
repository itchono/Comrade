# bot.py
import os
import dotenv
import discord

#import keep_alive

# text filtering
import re
import unidecode
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# download pfps
# import requests

# load variables
import comrade_cfg

dotenv.load_dotenv()

print('COMRADE BOT INITIALIZING...')

TOKEN = os.environ.get('TOKEN')
GUILD = os.environ.get('GUILD')

client = discord.Client()

print('Initializing parameters')

# init vars
kickList = comrade_cfg.kickList
kickVotes = comrade_cfg.kickVotes
LETHALITY = comrade_cfg.LETHALITY
THREATS = comrade_cfg.THREATS
OPS = comrade_cfg.OPS
KICK_SAFE = comrade_cfg.KICK_SAFE
KICK_REQ = comrade_cfg.KICK_REQ

def containsletters(string, check):
    res = True
    for i in range(len(check)-1):
        if string.find(check[i]) == -1 or string.find(check[i+1], string.find(check[i])) == -1:
            res = False
        
    return res

def loadVars():
    # if we ever need to reload vars
    global LETHALITY
    global THREATS
    global OPS
    global kickVotes
    global kickList
    global KICK_REQ
    global KICK_SAFE

    kickList = comrade_cfg.kickList
    kickVotes = comrade_cfg.kickVotes
    LETHALITY = comrade_cfg.LETHALITY
    THREATS = comrade_cfg.THREATS
    OPS = comrade_cfg.OPS
    KICK_SAFE = comrade_cfg.KICK_SAFE
    KICK_REQ = comrade_cfg.KICK_REQ


def writeInfo():
    # writes all variables to file again in order.
    with open('comrade_cfg.py', 'w') as cfg:
        cfg.write('kickList = ' + str(kickList) + '\n')
        cfg.write('kickVotes = ' + str(kickVotes) + '\n')
        cfg.write('LETHALITY = ' + str(LETHALITY) + '\n')
        cfg.write('THREATS = ' + str(THREATS) + '\n')
        cfg.write('OPS = ' + str(OPS) + '\n')
        cfg.write('KICK_SAFE = ' + str(KICK_SAFE) + '\n')
    
@client.event
async def on_message(message):
    global LETHALITY
    global THREATS
    global OPS
    global kickVotes
    global kickList
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
        elif 'henlo comrade' in message.content.lower():
            await message.channel.send('Hello')
        if '$comrade' in message.content.lower():
            parse = str(message.content).lstrip('$comrade').split()
            print(parse)
            if parse[0] == 'voteKick':
                user = str(message.mentions[0].id) # id of user to be kicked
                
                if not (str(message.author) in kickVotes[user] or str(message.author) in KICK_SAFE):
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
                    writeInfo()                       
                else:
                    await message.channel.send('You have already voted!')
                 
            elif parse[0] == 'lethal' and str(message.author) in OPS:
                LETHALITY = int(parse[1])
                writeInfo()
                if LETHALITY == 0:
                    await message.channel.send('Lethal mode has been deactivated.')
                else:
                    await message.channel.send('Lethality has been activated and set to {0}. This can cause destructive actions.'.format(LETHALITY))
                
            elif parse[0] == 'addThreat' and str(message.author) in OPS:
                user = str(message.mentions[0])
                THREATS.append(user)
                writeInfo()
                await message.channel.send('Threat Added.')
            elif parse[0] == 'removeThreat' and str(message.author) in OPS:
                user = str(message.mentions[0])
                if user in THREATS:
                    THREATS.remove(user)
                    writeInfo()
                await message.channel.send('Threat Added.')
            
            
            elif parse[0] == 'op' and str(message.author) in OPS:
                user = str(message.mentions[0])
                OPS.append(user)
                writeInfo()
                await message.channel.send('OP Added.')
            elif parse[0] == 'deop' and str(message.author) in OPS:
                user = str(message.mentions[0])
                if user in OPS:
                    OPS.remove(user)
                    writeInfo()
                await message.channel.send('OP Removed.')
                
            elif parse[0] == 'status':
                kicks = []
                for member in message.guild.members:
                    if kickList[str(member.id)] >= 1:
                        kicks.append(str(member) + ': ' + str(kickList[str(member.id)]))
                await message.channel.send('Threats: ' + str(THREATS) + '\nOPS:' + str(OPS) + '\nKick Requirement: ' + str(KICK_REQ) + "\nKick List: " + str(kicks) + "\nLethality: " + str(LETHALITY))
                
            elif parse[0] == 'kickReq' and str(message.author) in OPS:
                KICK_REQ = int(parse[1])
                writeInfo()
                await message.channel.send('Kick requirement has been set to {0} votes.'.format(KICK_REQ))
            elif parse[0] == 'resetKick' and str(message.author) in OPS:
                # resets Kicklist and kickvotes, sometimes also used when members join/leave etc
                for member in message.guild.members:
                    kickList[member.name] = 0
                    kickVotes[member.name] = []
                    writeInfo()
                await message.channel.send('Votes have been reset and votelist regenerated.')
            elif parse[0] == 'reloadVars' and str(message.author) in OPS:
                loadVars()
                await message.channel.send('All variables reloaded from file.')
                                      
                            

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

    print('Loading OPS and Threats')
    
    print('Constructing member list')

    for guild in client.guilds:
        if guild.name == GUILD:
            global kickList
            # populate kicklist
            num_mem = 0
            if (len(kickList.keys()) == 0):
                for member in guild.members:
                    num_mem +=1
                    # repopulate kicklist
                    kickList[member.id] = 0
                    kickVotes[member.id] = []
                writeInfo()
            # defunct - for avatars
            '''
            for member in guild.members:
                
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

    print('COMRADE is fully online.')

#keep_alive.keep_alive()
client.run(TOKEN)