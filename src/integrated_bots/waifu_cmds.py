import discord
from discord.ext import commands, tasks
from utils import *

import numpy as np
import random

#NAMES = ["Apple", "Banana", "Cow", "DNA", "E"]

class Waifu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.random_ID = np.random.randint(0, 150000)
        self.active_waifu = None

        self.produce_waifu.start()

    @commands.command()
    async def wclaim(self, ctx:commands.Context,*, waifuname):
        '''
        Claim your favourite waifu :)
        '''
        if waifuname == self.active_waifu:
            await ctx.send(f"Congrats {ctx.author.mention}, you claimed **{waifuname}**!")
            
            #should produce another waifu after the current one is claimed.
            self.produce_waifu
        else:
            await ctx.send(f"Try again")
    
    @commands.command()
    async def wdailygacha (self, ctx:commands.Context):
        '''
        gives u a random waifu
        '''

    @commands.command()
    async def wlistwaifus (self, ctx:commands.Context, user: discord.Member = None):
        '''
        lists your waifus
        '''

    @commands.command()
    async def wtradewaifus (self, ctx:commands.Context, *, user):
        '''
        Trade with someone?? idk how this would work tbh
        '''

    '''
    Timer based thing
    '''

    @tasks.loop(seconds=5)
    async def produce_waifu(self):

        waifu = random.choice(NAMES)

        self.active_waifu = waifu

        '''
        iraq_btw = self.bot.get_guild(419214713252216848)
        west_korea = iraq_btw.get_channel(522428899184082945)
        '''

        # NOTE: This is just for bot development; NOT when we actually deploy
        test_btw = self.bot.get_guild(709954286376976425)
        west_korea = test_btw.get_channel(742181992824700989)

        await west_korea.send(f"Yo a waifu spawned: {waifu}")

    @produce_waifu.before_loop
    async def before(self):
        await self.bot.wait_until_ready()



