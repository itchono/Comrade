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

        await self.rebuildcache() # refresh cache

        await ctx.send('Emote {} was added. you can call it using :{}:.'.format(name.lower(), name.lower()))
        
    @commands.command()
    @commands.check(isnotSuperThreat)
    async def emoteCall(self, ctx, name):
        '''
        Calls an emote by name. You can equivalently call using :emotename:
        '''
        try:
            embed = discord.Embed()
            embed.set_image(url=self.EMOTE_CACHE[message.guild.id][name])
            await ctx.send(embed=embed)
        except:
            pass

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        When bot is loaded
        '''
        await self.rebuildcache()
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        '''
        Emote listener
        '''

        if re.search(":*:", message.content.lower()):
            # see if emote header is in the 

            s = message.content.lower()
            e = s[s.find(":")+1:s.find(":",s.find(":")+1)]

            c = self.bot.get_context(message)
            await self.emoteCall(c, e) # run through command to get checks

            
    