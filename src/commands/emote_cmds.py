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
        
            await log(g, "Emote Cache Built Successfully.")

    @commands.command()
    @commands.guild_only()
    async def addEmote(self, ctx: commands.Context, name, *args):
        '''
        Adds a custom emote to the Comrade Emote System
        '''
        if len(ctx.message.attachments) > 0:
            u = ctx.message.attachments[0].url
        else:
            u = args[(len(args)-1)]

        if not name.lower() in self.EMOTE_CACHE[ctx.guild.id]:
            emoteDirectory = await getChannel(ctx.guild, 'emote directory')
            await emoteDirectory.send('{}\n{}'.format(name.lower(), u))

            await self.rebuildcache() # refresh cache

            await ctx.send('Emote `{}` was added. you can call it using `:{}:`'.format(name.lower(), name.lower()))
        else:
            await reactX(ctx)
            await ctx.send('Emote `{}` already exists! Contact a mod to get this fixed.'.format(name.lower()))

    @commands.command()
    @commands.guild_only()
    async def listEmotes(self, ctx : commands.Context):
        '''
        Lists all emotes in the server, sent to DMs
        '''
        emotes = list(self.EMOTE_CACHE[ctx.guild.id].keys())

        break_lim = 30

        for i in range(0, len(emotes), break_lim): # break into chunks
            e = discord.Embed(title = "Custom Emotes for {} ({} to {})".format(ctx.guild.name, i+1, (i+1+break_lim if i+1+break_lim < len(emotes) else len(emotes))))
            
            for k in emotes[i:i + break_lim]: e.add_field(name=k, value="[Link]({})".format(self.EMOTE_CACHE[ctx.guild.id][k]))
            
            await DM(s="", user=ctx.author, embed=e)
        await delSend("Check your DMs {}".format(ctx.author.mention), ctx.channel)

    @commands.command()
    @commands.guild_only()
    @commands.check(isOP)
    async def removeEmote(self, ctx: commands.Context, name):
        '''
        Removes a custom emote from the Comrade Emote System
        '''
        if name.lower() in self.EMOTE_CACHE[ctx.guild.id]:
            async for m in (await getChannel(ctx.guild, 'emote directory')).history(limit = None):
                if name.lower() in m.content:
                    await m.delete()
                    del self.EMOTE_CACHE[ctx.guild.id][name.lower()]
                    continue
            await ctx.send("Emote `{}` was removed.".format(name.lower()))
        else:
            await ctx.send("Emote `{}` was not found.".format(name.lower()))

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        When bot is loaded
        '''
        await self.rebuildcache()

    async def emote(self, ctx : commands.Context, e:str):
        '''
        Sends an emote into a context.
        '''
        try:
            embed = discord.Embed()
            embed.set_image(url=self.EMOTE_CACHE[ctx.guild.id][e])
            await ctx.send(embed=embed)
        except:
            await reactX(ctx)
            similar = [i for i in self.EMOTE_CACHE[ctx.guild.id] if fuzz.partial_ratio(i, e) > 60]

            embed = discord.Embed(description="Emote `{}` not found. Did you mean one of the following?".format(e))

            if similar != []:
                for k in similar: embed.add_field(name="Suggestion", value=":{}:".format(k))
            else:
                directory = await getChannel(ctx.guild, 'emote directory')
                embed.add_field(name="Sorry, no similar results were found.", value="See {}, or type `{}listemotes` for a list of all emotes.".format(directory.mention, BOT_PREFIX))

            await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        '''
        Emote listener [works with bots too]
        '''
        if message.content and message.guild and message.content[0] == ':' and message.content[-1] == ':':
            await self.emote(await self.bot.get_context(message), message.content.lower().strip(':'))

            
                    


            
    