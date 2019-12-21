import os
from main_serenity import client

async def writeInfo():
    # writes all variables to file again in order.

    if os.path.exists("comrade_cfg.py"):
        os.remove("comrade_cfg.py")

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
            cfg.write('USER_BANNED_WORDS = ' + str(USER_BANNED_WORDS) + '\n')
        await client.get_guild(419214713252216848).get_channel(446457522862161920).send("Data Written Successfully.")
    else:
        print("The file does not exist")
        await client.get_guild(419214713252216848).get_channel(446457522862161920).send("Data could not be written.")

async def dailyMSG(force = False):
    await client.wait_until_ready()

    global LAST_DAILY

    while not client.is_closed():
        if datetime.datetime.utcnow().date() > LAST_DAILY and ((datetime.datetime.utcnow().hour > 11 and datetime.datetime.utcnow().hour < 13) or force):

            # MESSAGE CLEANSE
            #await cleanMSG()

            # Announcement
            dailyAnnounce = 'Good morning everyone!\nToday is {}. Have a prosperous day! <:FeelsProsperousMan:419256328465285131>'.format(datetime.datetime.utcnow().date())
            await client.get_guild(419214713252216848).get_channel(419214713755402262).send(dailyAnnounce)
            LAST_DAILY = datetime.datetime.utcnow().date()
            await asyncio.sleep(5)
            await writeInfo()
            await asyncio.sleep(5)
            await client.get_guild(419214713252216848).get_channel(446457522862161920).send("Daily Announcement Made. Current LAST_DAILY = {}".format(datetime.datetime.strptime(comrade_cfg.LAST_DAILY, '%Y-%m-%d').date()))
        
            # Daily 
            await dailyRole()

            # VOTE RESET
            global kickList
            global kickVotes
            for member in client.get_guild(419214713252216848).members:
                kickList[member.id] = 0
                kickVotes[member.id] = []
            await writeInfo()
        
        await asyncio.sleep(60)

async def cleanMSG():
    for channel in client.get_guild(419214713252216848).text_channels:
        yesterday = datetime.datetime.now()-datetime.timedelta(days=1)
        async for msg in channel.history(limit=None,after=yesterday):
            if msg.author == client.user:
                await msg.delete()

async def quarantine(user, message):
    currRoles = user.roles
    isQ = False
    for r in currRoles:
        if r.id == 613106246874038274: # quarantine role
            isQ = True
            currRoles.remove(r)
            # remove the role if quarantined
        elif r.id == 419215295232868361: # regular role
            currRoles.remove(r)
    if isQ:
        currRoles.append(message.guild.get_role(419215295232868361))
        await message.channel.send('{} has been returned to society.'.format(user.name))
    else:
        currRoles.append(message.guild.get_role(613106246874038274))
        await message.channel.send('{} has been quarantined.'.format(user.name))
    await user.edit(roles=currRoles)

async def dailyRole():
    members = client.get_guild(419214713252216848).members
    chosenone = random.randint(0, len(members)-1)

    s = members[chosenone].mention

    for member in client.get_guild(419214713252216848).members:
        currRoles = member.roles
        for r in currRoles:
            if r.id == 655670092679479296: # Daily
                currRoles.remove(r)
                await member.edit(roles=currRoles)
                # remove the role if Daily'd
        if member == members[chosenone]:
            currRoles.append(client.get_guild(419214713252216848).get_role(655670092679479296))
            await member.edit(roles=currRoles)
            await client.get_guild(419214713252216848).get_channel(419214713755402262).send('Today\'s daily member is {}'.format(s))
        
async def sentinelFilter(message):
    # intelligent message filtering system
    query = re.sub('\W+','', unidecode.unidecode(message.content.lower()))
    for word in set(BANNED_WORDS).union(set(USER_BANNED_WORDS[message.author.id])):
        if word in query or (fuzz.partial_ratio(word, query) > 75 and LETHALITY >= 2.1):
            await message.delete()
            print('Message purged for bad word:\n', str(message.content))
            await infraction(message, message.author.id, 0.5)

    
    if u"\U0001F1ED" in message.content and THREATS[message.author.id] >= 2: # H filter
        await message.delete()
        print('Message with emoji purged:\n', str(message.content))
        await infraction(message, message.author.id, 0.5)

    if (len(message.attachments) > 0 or len(message.embeds) > 0) and THREATS[message.author.id] >= 2:
        print('Attachment Purged')
        await message.delete()
        await infraction(message, message.author.id, 0.5)

async def infraction(message, user, weight):
    kickList[user] += weight
    await message.channel.send('Yare yare daze\nInfraction committed by {0} ({2}/{1}).'.format(str(message.author.name), float(KICK_REQ), float(kickList[user])))
    if (kickList[user] >= KICK_REQ):
        member = message.guild.get_member(user) # more efficient code
        print(member)
        if LETHALITY >= 1:
            kickList[user] = 0
            await message.channel.send('@' + str(member.name)+ ' has been kicked successfully')
            await message.guild.kick(member)
        else:
            await message.channel.send('Lethal mode has been disabled. Please enable it with $comrade lethal <level>')
    await writeInfo()                       


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