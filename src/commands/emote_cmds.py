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
        e = discord.Embed(title = "Custom Emotes for {} ({})".format(ctx.guild.name, len(self.EMOTE_CACHE[ctx.guild.id])))

        for k in self.EMOTE_CACHE[ctx.guild.id]:
            e.add_field(name=k, value="[Link]({})".format(self.EMOTE_CACHE[ctx.guild.id][k]))

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

    async def emote(self, channel : discord.TextChannel, e:str):
        '''
        Sends an emote into a channel. TODO
        '''
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        '''
        Emote listener
        '''
        if message.content and message.content[0] == ':' and message.content[-1] == ':':
            # TEST: Tried removing self-check

            s = message.content.lower()
            e = s.strip(':')

            try:
                embed = discord.Embed()
                embed.set_image(url=self.EMOTE_CACHE[message.guild.id][e])
                await message.channel.send(embed=embed)
            except:
                await reactX(await self.bot.get_context(message))
                similar = [i for i in self.EMOTE_CACHE[message.guild.id] if fuzz.partial_ratio(i, e) > 60]

                embed = discord.Embed(description="Emote `{}` not found. Did you mean one of the following?".format(e))

                if similar != []:
                    for k in similar:
                        embed.add_field(name="Suggestion", value=":{}:".format(k))
                else:
                    directory = await getChannel(message.guild, 'emote directory')
                    embed.add_field(name="Sorry, no similar results were found.", value="See {} for a list of all emotes.".format(directory.mention))

                await message.channel.send(embed=embed)
                    


            
    