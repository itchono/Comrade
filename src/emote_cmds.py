from utils.utilities import *
from utils.mongo_interface import *

import re

class Emotes(commands.Cog):
    '''
    Contributed by Slyflare
    '''
    def __init__(self, bot):
        self.bot = bot
        self.EMOTE_CACHE = {}
        self._last_member = None


    async def rebuildcache(self):
        '''
        Rebuilds emote cache.
        '''
        self.EMOTE_CACHE = {}

        for g in self.bot.guilds:
            self.EMOTE_CACHE[g.id] = {}
            directory = await getChannel(g, 'emote directory')
            
            async for e in directory.history(limit=None):
                self.EMOTE_CACHE[g.id][e.content.split("\n")[0]] = e.content.split("\n")[1]
        
        print("Emote Cache Built Successfully.")

    @commands.command()
    async def addEmote(self, ctx, name, *args):
        '''
        Adds a custom emote to the Comrade Emote System
        '''
        if len(ctx.message.attachments) > 0:
            u = ctx.message.attachments[0].url
        else:
            u = args[(len(args)-1)]

        emoteDirectory = await getChannel(ctx.guild, 'emote directory')
        await emoteDirectory.send('{}\n{}'.format(name.lower(), u))

        await rebuildcache(ctx) # refresh cache

        await ctx.send('Emote {} was added. you can call it using :{}:.'.format(name.lower(), name.lower()))
        
    @commands.command()
    @commands.check(isnotSuperThreat)
    async def emoteCall(self, ctx, name):
        directory = await getChannel(ctx.guild, 'emote directory')
        async for e in directory.history(limit=None):
            if name.lower() in e.content.split("\n")[0]:
                emote = e.content.split("\n")[1]
                await ctx.send(emote)
            else:
                await ctx.send('{} exist not'.format(name))

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        When bot is loaded
        '''


    
    @commands.Cog.listener()
    async def on_message(self, message: discord.message):

        if re.search(":*:", message.content.lower()):
            # see if emote header is in the 


        if ':' in message.content.lower():
            e = message.content.split(':')
            e = e[1]
            directory = await getChannel(message.guild, 'emote directory')
            name = []
            async for i in directory.history(limit=None):
                temp = i.content.split('\n')
                name.append(temp[0])
            async for p in directory.history(limit=None):
                if e in p.content.split('\n'):
                    emote = p.content.split('\n')[1]
                    await message.channel.send(emote)
                    embed = discord.Embed()
                    embed.set_image(url=emoteURL)
                    await message.channel.send(embed=embed)
    