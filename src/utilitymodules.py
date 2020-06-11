'''
Comrade Bot - Additional Utility Modules

'''

# I: External Library Imports
import discord
from datetime import datetime # Time func

'''
FUNCTIONS
'''
async def generateRequiem(message: discord.message, mode='NonRole'):
    PURGE_DATE = datetime.datetime(2099, 1, 1)
    # SET this first

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
            async for msg in channel.history(limit=None,after=PURGE_DATE):
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
            async for msg in channel.history(limit=None,after=PURGE_DATE):
                for member in members:
                    if msg.author == member:
                        members.remove(member)
        return members