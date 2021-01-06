'''
$c remind 6h <name>
>>> you will be reminded to <name> on <current date + 6h>
'''

import discord
from discord.ext import commands, tasks

class Reminders(commands.Cog):
    '''
    Remind you in the future
    '''
    def __init__(self, bot):
        self.bot = bot

    
