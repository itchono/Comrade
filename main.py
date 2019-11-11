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

import asyncio
import datetime

# load variables
import comrade_cfg

# download pfps
import requests

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
ON_TIME = datetime.datetime.now()
LAST_DAILY = datetime.datetime.strptime(comrade_cfg.LAST_DAILY, '%Y-%m-%d').date()
PURGE = []
v_list = comrade_cfg.v_list
lost_nnn = comrade_cfg.lost_nnn


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
    global LAST_DAILY
    global v_list
    global lost_nnn

    kickList = comrade_cfg.kickList
    kickVotes = comrade_cfg.kickVotes
    LETHALITY = comrade_cfg.LETHALITY
    THREATS = comrade_cfg.THREATS
    OPS = comrade_cfg.OPS
    KICK_SAFE = comrade_cfg.KICK_SAFE
    KICK_REQ = comrade_cfg.KICK_REQ
    BANNED_WORDS = comrade_cfg.BANNED_WORDS
    LAST_DAILY = datetime.datetime.strptime(comrade_cfg.LAST_DAILY, '%Y-%m-%d').date()
    PURGE = [client.get_guild(419214713252216848).get_member(i) for i in comrade_cfg.PURGE]
    v_list = comrade_cfg.v_list
    lost_nnn = comrade_cfg.lost_nnn

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
        cfg.write('PURGE = ' + str([i.id for i in PURGE]) + '\n')
        cfg.write('LAST_DAILY = \"' + str(LAST_DAILY) + '\"\n')
        cfg.write('v_list = ' + str(v_list) + '\n')
        cfg.write('lost_nnn = ' + str(lost_nnn) + '\n')

async def dailyMSG():
    await client.wait_until_ready()

    global LAST_DAILY

    dailyAnnounce = 'Good morning everyone!\nToday is {}. Have a prosperous day! <:FeelsProsperousMan:419256328465285131>'.format(datetime.datetime.now().date())

    while not client.is_closed():
        if datetime.datetime.now().date() > LAST_DAILY and datetime.datetime.now().hour > 6:
            await client.get_guild(419214713252216848).get_channel(419214713755402262).send(dailyAnnounce)
            LAST_DAILY = datetime.datetime.now().date()
            writeInfo()
        await asyncio.sleep(60)

async def sentinelFilter(message):
    # intelligent message filtering system
    query = re.sub('\W+','', unidecode.unidecode(message.content.lower()))
    for word in BANNED_WORDS:
        if word in query or fuzz.partial_ratio(word, query) > 75:
            await message.delete()
            print('Message purged:\n', str(message.content))
    
    if u"\U0001F1ED" in message.content: # H filter
        await message.delete()
        print('Message with emoji purged:\n', str(message.content))


async def generateRequiem(message: discord.message, mode='NonRole'):
    # produces a list of members to be purged

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
    global PURGE
    global v_list

    isOP = (message.author.id) in OPS
    isOwner = message.author == message.guild.get_member(66137108124803072) # owner only commands
    
    if message.author != client.user:
        #failsafe against self response
        
        # $SENTINEL
        if (LETHALITY >= 2 and message.author.id in THREATS):
            await sentinelFilter(message)
            
        # $JERICHO
        if 'hello comrade' in message.content.lower():
            await message.channel.send('Henlo')
        elif 'henlo comrade' in message.content.lower():
            await message.channel.send('Hello')

        if message.mention_everyone:
            print('yo')
            for e in message.guild.emojis:
                if e.name == 'pong':
                    await message.add_reaction(e)

        # COMMANDS
        if '$comrade' in message.content.lower():
            parse = str(message.content).lstrip('$comrade').split()
            if parse[0] == 'voteKick' or parse[0] == 'vibeCheck':
                user = message.mentions[0].id # id of user to be kicked
                
                if not (message.author.id in kickVotes[user] or message.mentions[0].id in KICK_SAFE):
                    kickList[user] += 1
                    kickVotes[user].append(message.author.id)
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
                if ((message.author.id) in kickVotes[user]):
                    kickList[user] -= 1
                    kickVotes[user].remove(message.author.id)
                    await message.channel.send('Vote removed for {0} ({2}/{1}).'.format(str(message.mentions[0].name), int(KICK_REQ), int(kickList[user])))
                    writeInfo()
                else:
                    await message.channel.send('You have not voted to kick ' + str(message.mentions[0].name))
                 
            elif parse[0] == 'lethal' and isOP:
                LETHALITY = int(parse[1])
                writeInfo()
                if LETHALITY == 0:
                    await message.channel.send('Lethal mode has been deactivated.')
                else:
                    await message.channel.send('Lethality has been activated and set to {0}. This can cause destructive actions.'.format(LETHALITY))
                
            elif parse[0] == 'addThreat' and isOP:
                user = message.mentions[0].id
                THREATS.append(user)
                writeInfo()
                await message.channel.send('Threat Added.')

            elif parse[0] == 'removeThreat' and isOP:
                user = message.mentions[0].id
                if user in THREATS:
                    THREATS.remove(user)
                    writeInfo()
                await message.channel.send('Threat Added.')
            
            elif parse[0] == 'op' and isOP:
                user = message.mentions[0].id
                OPS.append(user)
                writeInfo()
                await message.channel.send('OP Added.')
            elif parse[0] == 'deop' and isOP:
                user = message.mentions[0].id
                if user in OPS:
                    OPS.remove(user)
                    writeInfo()
                await message.channel.send('OP Removed.')
                
            elif parse[0] == 'status':
                kicks = []
                for member in message.guild.members:
                    if kickList[member.id] >= 1:
                        kicks.append(str(member) + ': ' + str(kickList[member.id]))
                disp_OPS = str([str(message.guild.get_member(i)) for i in OPS])
                disp_THREATS = str([str(message.guild.get_member(i)) for i in THREATS])
                curr_time = datetime.datetime.now()
                dt = curr_time - ON_TIME

                await message.channel.send('OPS: {0}\nThreats: {1}\nKick Votes: {2}\nKick Requirement: {3}\nLethality: {4}\nUptime: {5}\n'.format(disp_OPS, disp_THREATS, str(kicks), KICK_REQ, LETHALITY, str(dt)))
                
            elif parse[0] == 'kickReq' and isOP:
                KICK_REQ = int(parse[1]) if int(parse[1]) >= 1 else KICK_REQ
                writeInfo()
                await message.channel.send('Kick requirement has been set to {0} votes.'.format(KICK_REQ))
            elif parse[0] == 'resetKick' and isOP:
                # resets Kicklist and kickvotes, sometimes also used when members join/leave etc
                for member in message.guild.members:
                    kickList[member.id] = 0
                    kickVotes[member.id] = []
                writeInfo()
                await message.channel.send('Votes have been reset and votelist regenerated.')

            elif parse[0] == 'reloadVars' and isOwner:
                loadVars()
                await message.channel.send('All variables reloaded from file.')

            elif parse[0] == 'addBanWord' and isOP:
                BANNED_WORDS.append(parse[1])
                await message.channel.send(parse[1], ' has been added to blacklist.')
                writeInfo()
            elif parse[0] == 'removeBanWord' and isOP:
                BANNED_WORDS.remove(parse[1])
                await message.channel.send(parse[1], ' has been removed from blacklist.')
                writeInfo()

            elif parse[0] == 'addBanSafe' and isOwner:
                KICK_SAFE.append((message.mentions[0].id))
                await message.channel.send(message.mentions[0].name + ' has been added to safelist.')
                writeInfo()

            elif parse[0] == 'removeBanSafe' and isOwner:
                KICK_SAFE.remove((message.mentions[0].id))
                await message.channel.send(message.mentions[0].name +  ' has been added to safelist.')
                writeInfo()   

            elif parse[0] == 'genRequiem' and isOwner:
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
            
            elif parse[0] == 'PURGE' and isOwner:
                if LETHALITY >= 3:
                    await message.channel.send('Purge started. Preparing to kick {} members'.format(len(PURGE)))
                    for member in PURGE:
                        await message.guild.kick(member)
                    await message.channel.send('Purge complete. Please reset votelists to restore normal functionality.')
                else:
                    await message.channel.send('Please set lethality to level 3 or above to continue. {} members will be kicked.'.format(len(PURGE)))

            elif parse[0] == 'lostVirginity':
                v_list.append(message.mentions[0].id)
                await message.channel.send(message.mentions[0].name + ', congrats!')
                writeInfo()

            elif parse[0] == 'listNonVirgins':
                mem = [message.guild.get_member(i).name for i in v_list]
                await message.channel.send(str(mem))

            elif parse[0] == 'failedNNN':
                lost_nnn.add(message.mentions[0].id)
                await message.channel.send(message.mentions[0].name + ', you lost NNN!')
                writeInfo()

            elif parse[0] == 'listLostNNN':
                mem = [message.guild.get_member(i).name for i in lost_nnn]
                await message.channel.send(str(mem))
            else:
                response = requests.get('https://raw.githubusercontent.com/wiki/itchono/Comrade/Home.md')
                await message.channel.send(str(response.content).replace('\n','\t'))

@client.event
async def on_message_edit(messageOG, messageNEW):  
    if LETHALITY >= 2 and messageNEW.author != client.user and not messageNEW.author.id in THREATS:
        await sentinelFilter(messageNEW)
            
async def getPics(guild):
    # used to retrieve all pfps and links
    with open('avatars/avatarlist.txt', 'wb') as file:
        for member in guild.members:
            url = "https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(member)
            
            r = requests.get(url)
            with open('avatars/avatar{0}.png'.format(member.id), 'wb') as outfile:
                outfile.write(r.content)
            file.write(url + '\n')

@client.event
async def on_ready():
    print('Loading OPS and Threats')
    
    print('Constructing member list')
    global PURGE
    PURGE = [client.get_guild(419214713252216848).get_member(i) for i in comrade_cfg.PURGE]

    for guild in client.guilds:
        if guild.name == GUILD:
            global kickList
            global kickVotes
            # populate kicklist
            num_mem = 0
            if (len(kickList) == 0):
                for member in guild.members:
                    num_mem +=1
                    # repopulate kicklist
                    kickList[member.id] = 0
                    kickVotes[member.id] = []
                writeInfo()
            print(len(guild.members), "members loaded.")
            print(num_mem, "new members appended to list.")
            break
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})')
        
    await client.change_presence(status=discord.Status.online, activity=discord.Game("Upholding Communism"))

    print('COMRADE is fully online.')

# create server
keep_alive.keep_alive()
# create tasks
client.loop.create_task(dailyMSG())

# finally, start the bot
client.run(TOKEN)




