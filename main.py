# bot.py
import os
import dotenv
import discord

import keep_alive

# text filtering
import re
import unidecode
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

import datetime

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
BANNED_WORDS = comrade_cfg.BANNED_WORDS
PURGE = comrade_cfg.PURGE

''' defunct text filtering
def containsletters(string, check):
    res = True
    for i in range(len(check)-1):
        if string.find(check[i]) == -1 or string.find(check[i+1], string.find(check[i])) == -1:
            res = False
        
    return res
'''

def loadVars():
    # if we ever need to reload vars
    global LETHALITY
    global THREATS
    global OPS
    global kickVotes
    global kickList
    global KICK_REQ
    global KICK_SAFE
    global BANNED_WORDS
    global PURGE

    kickList = comrade_cfg.kickList
    kickVotes = comrade_cfg.kickVotes
    LETHALITY = comrade_cfg.LETHALITY
    THREATS = comrade_cfg.THREATS
    OPS = comrade_cfg.OPS
    KICK_SAFE = comrade_cfg.KICK_SAFE
    KICK_REQ = comrade_cfg.KICK_REQ
    BANNED_WORDS = comrade_cfg.BANNED_WORDS
    PURGE = comrade_cfg.PURGE


def writeInfo():
    # writes all variables to file again in order.
    with open('comrade_cfg.py', 'w') as cfg:
        cfg.write('kickList = ' + str(kickList) + '\n')
        cfg.write('kickVotes = ' + str(kickVotes) + '\n')
        cfg.write('LETHALITY = ' + str(LETHALITY) + '\n')
        cfg.write('THREATS = ' + str(THREATS) + '\n')
        cfg.write('OPS = ' + str(OPS) + '\n')
        cfg.write('KICK_REQ = ' + str(KICK_REQ) + '\n')
        cfg.write('KICK_SAFE = ' + str(KICK_SAFE) + '\n')
        cfg.write('BANNED_WORDS = ' + str(BANNED_WORDS) + '\n')
        cfg.write('PURGE = ' + str(PURGE) + '\n')


async def generateRequiem(message: discord.message, mode='NonRole'):

    if mode == 'NonRole':
        # produces a list of members to be purged
        # takes in server

        non_roled = []
        for member in message.guild.members:
            if str(member.roles) == '[<Role id=419214713252216848 name=\'@everyone\'>, <Role id=419215295232868361 name=\'Communism is the only Role\'>]':
                non_roled.append(member)
        
        names = []
        for member in non_roled:
            names.append(str(member))
        await message.channel.send('Preliminary List of members without other roles:')
        await message.channel.send(str(names))

        await message.channel.send('Trimming. This will take a while.')
        for channel in message.guild.text_channels:
            async for msg in channel.history(limit=None,after=datetime.datetime(2019, 10, 8)):
                for member in non_roled:
                    if msg.author == member:
                        await message.channel.send(str('Member found: {0} in message sent at {1}:\n{2}'.format(non_roled.pop(non_roled.index(member)), str(msg.created_at), msg.content)))

        return non_roled
    elif mode == 'All':
        # produces a list of members to be purged
        # takes in server

        members = []
        for member in message.guild.members:
            members.append(member)

        await message.channel.send('Scanning ALL members This will take a while.')
        for channel in message.guild.text_channels:
            async for msg in channel.history(limit=None,after=datetime.datetime(2019, 10, 8)):
                for member in members:
                    if msg.author == member:
                        members.remove(member)

        return members
    
@client.event
async def on_message(message):
    global LETHALITY
    global THREATS
    global OPS
    global kickVotes
    global kickList
    global KICK_REQ
    global BANNED_WORDS
    
    if message.author != client.user:
        #failsafe against self response
        
        # $SENTINEL
        if (LETHALITY >= 2 and str(message.author) in THREATS):
            query = re.sub('\W+','', unidecode.unidecode(message.content.lower()))
            for word in BANNED_WORDS:
                if word in query or fuzz.partial_ratio(word, query) > 75:
                    await message.delete()
                    print('Message purged:\n', str(message.content))
         
            if u"\U0001F1ED" in message.content:
                await message.delete()
                print('Message with emoji purged:\n', str(message.content))
            
        # $JERICHO
        if 'hello comrade' in message.content.lower():
            await message.channel.send('Henlo')
        elif 'henlo comrade' in message.content.lower():
            await message.channel.send('Hello')
       
       
        if '$comrade' in message.content.lower():
            parse = str(message.content).lstrip('$comrade').split()
            if parse[0] == 'voteKick':
                user = message.mentions[0].id # id of user to be kicked
                
                if not (str(message.author) in kickVotes[user] or str(message.mentions[0]) in KICK_SAFE):
                    kickList[user] += 1
                    kickVotes[user].append(str(message.author))
                    await message.channel.send('Vote added for {0} ({2}/{1}).'.format(str(message.mentions[0].name), int(KICK_REQ), int(kickList[user])))
                    if (kickList[user] >= KICK_REQ):
                        member = message.guild.get_member(user) # more efficient code
                        print(member)
                        if LETHALITY >= 1:
                            kickList[user] = 0
                            await message.channel.send('@' + str(member.name)+ ' has been kicked successfully')
                            await message.guild.kick(member)
                        else:
                            await message.channel.send('Lethal mode has been disabled. Please enable it with $comrade lethal <level>')
                    writeInfo()                       
                else:
                    await message.channel.send('You have already voted!')
            
            elif parse[0] == 'unKick':
                user = message.mentions[0].id # id of user to be kicked
                if (str(message.author) in kickVotes[user]):
                    kickList[user] -= 1
                    kickVotes[user].remove(str(message.author))
                    await message.channel.send('Vote removed for {0} ({2}/{1}).'.format(str(message.mentions[0].name), int(KICK_REQ), int(kickList[user])))
                    writeInfo()
                else:
                    await message.channel.send('You have not voted to kick ' + str(message.mentions[0].name))
                 
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
                    if kickList[member.id] >= 1:
                        kicks.append(str(member) + ': ' + str(kickList[member.id]))
                await message.channel.send('Threats: ' + str(THREATS) + '\nOPS:' + str(OPS) + '\nKick Requirement: ' + str(KICK_REQ) + "\nKick List: " + str(kicks) + "\nLethality: " + str(LETHALITY))
                
            elif parse[0] == 'kickReq' and str(message.author) in OPS:
                KICK_REQ = int(parse[1])
                writeInfo()
                await message.channel.send('Kick requirement has been set to {0} votes.'.format(KICK_REQ))
            elif parse[0] == 'resetKick' and str(message.author) in OPS:
                # resets Kicklist and kickvotes, sometimes also used when members join/leave etc
                for member in message.guild.members:
                    kickList[member.id] = 0
                    kickVotes[member.id] = []
                    writeInfo()
                await message.channel.send('Votes have been reset and votelist regenerated.')
            elif parse[0] == 'reloadVars' and str(message.author) in OPS:
                loadVars()
                await message.channel.send('All variables reloaded from file.')

            elif parse[0] == 'addBanWord' and str(message.author) in OPS:
                BANNED_WORDS.append(parse[1])
                await message.channel.send(parse[1], ' has been added to blacklist.')
                writeInfo()
            elif parse[0] == 'removeBanWord' and str(message.author) in OPS:
                BANNED_WORDS.remove(parse[1])
                await message.channel.send(parse[1], ' has been removed from blacklist.')
                writeInfo()

            elif parse[0] == 'addBanSafe' and str(message.author) in OPS:
                KICK_SAFE.append(parse[1])
                await message.channel.send(parse[1], ' has been added to safelist.')
                writeInfo()
            elif parse[0] == 'removeBanSafe' and str(message.author) in OPS:
                KICK_SAFE.remove(parse[1])
                await message.channel.send(parse[1], ' has been added to safelist.')
                writeInfo()   

            elif parse[0] == 'genRequiem':
                await message.channel.send('Generating purge list. Please wait.')
                purge = await generateRequiem(message, str(parse[1]))
                names = []
                for member in purge:
                    names.append(str(member))
                await message.channel.send('Pruned list generated.')
                await message.channel.send(str(names))
                PURGE = purge
                writeInfo()
                await message.channel.send('{0} members loaded for purge. Execute purge with $comrade PURGE'.format(len(PURGE)))


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
            print(len(guild.members), "members loaded.")
            print(num_mem, "new members added to list.")
            break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})')
        
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Upholding Communism"))

    print('COMRADE is fully online.')

keep_alive.keep_alive()
client.run(TOKEN)