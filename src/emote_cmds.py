from utils.utilities import *
from utils.mongo_interface import *

import re
from fuzzywuzzy import fuzz

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
                self.EMOTE_CACHE[g.id][e.content.lower().split("\n")[0]] = e.content.split("\n")[1]
        
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

        await ctx.send('Emote {} was added. you can call it using :{}:'.format(name.lower(), name.lower()))

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
        if not message.author.bot and message.content[0] == ':' and message.content[-1] == ':':
            # see if emote header is in the 

            s = message.content.lower()
            e = s.strip(':')

            try:
                embed = discord.Embed()
                embed.set_image(url=self.EMOTE_CACHE[message.guild.id][e])
                await message.channel.send(embed=embed)
            except:
                await reactX(await self.bot.get_context(message))
                similar = [i for i in self.EMOTE_CACHE[message.guild.id] if fuzz.ratio(i, e) > 60]

                embed = discord.Embed(description="Emote not found. Did you mean one of the following?")

                if similar != []:
                    for k in similar:
                        embed.add_field(name="Suggestion", value=":{}:".format(k))
                else:
                    directory = await getChannel(message.guild, 'emote directory')
                    embed.add_field(name="Sorry, no similar results were found.", value="See {} for a list of all emotes.".format(directory.mention))

                await message.channel.send(embed=embed)
                    


            
    