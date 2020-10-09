import discord
from discord.ext import commands
from utils import *

import re, requests
from fuzzywuzzy import fuzz # NOTE: install python-Levenshtein for faster results.

import bson, io, time, random

from utils.checks.other_checks import match_url

class Emotes(commands.Cog):
    '''
    Contributed by Slyflare
    '''
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command()
    @commands.guild_only()
    async def addEmoji(self, ctx:commands.Context, name, url=None):
        '''
        Adds an emoji to the system
        '''
        try:
            if not url: url = ctx.message.attachments[0].url
        except:
            if not match_url(url): await ctx.send("Invalid URL Provided."); return

        if not DBcollection("Emotes").find_one({"name":name, "server":ctx.guild.id}):

            binImage = requests.get(url).content # binaries

            DBcollection("Emotes").insert_one(
                {"name":name,
                "server":ctx.guild.id,
                "type":"inline",
                "file":binImage})
            await self.inject(ctx, name)
        else:
            await reactX(ctx)
            await ctx.send('Emote `{}` already exists! Contact a mod to get this fixed.'.format(name))


    @commands.command()
    @commands.guild_only()
    async def addEmote(self, ctx: commands.Context, name, url=None):
        '''
        Adds a custom emote to the Comrade Emote System
        '''
        try:
            if not url: url = ctx.message.attachments[0].url
        except:
            if not match_url(url): await ctx.send("Invalid URL Provided."); return

        if not DBcollection("Emotes").find_one({"name":name.lower(), "server":ctx.guild.id}):
            # make sure it doesn't already exist

            binImage = requests.get(url).content # binaries

            DBcollection("Emotes").insert_one(
                {"name":name,
                "server":ctx.guild.id,
                "type":"big",
                "file":binImage})
            
            await ctx.send(f'Emote `{name.lower()}` was added. you can call it using `:{name.lower()}:`')
        
        else:
            await reactX(ctx)
            await ctx.send('Emote `{}` already exists! Contact a mod to get this fixed.'.format(name.lower()))


    async def inject(self, ctx:commands.Context, name):
        '''
        Attempts to inject image into the server's list of emoji, sending it afterward
        '''

        tstart = time.perf_counter()

        if document := DBcollection("Emotes").find_one({"name":name, "server":ctx.guild.id}):

            LIMIT = 3
            
            ## UNLOAD EMOJI
            if len(ctx.guild.emojis) >= LIMIT-1:

                unload = random.choice(ctx.guild.emojis) # emoji to be unloaded

                if not DBcollection("Emotes").find_one({"name":unload.name, "server":ctx.guild.id}):
                    # If not loaded, we must first database it

                    binImage = requests.get(unload.url).content # binaries

                    DBcollection("Emotes").insert_one(
                        {"name":unload.name,
                        "server":ctx.guild.id,
                        "type":"inline",
                        "file":binImage})
                
                await unload.delete(reason=f"Unloading emoji to make space for {name}")

            ## LOAD NEW EMOJI
            data = document["file"]

            await ctx.guild.create_custom_emoji(name=name, image=data, reason=f"Requested by user {ctx.author.display_name}")
            ## binary data

            tend = time.perf_counter()

            await ctx.send(f"Injection Complete in T = {round(tend - tstart, 3)}s")

            e = discord.utils.get(ctx.guild.emojis, name=name)

            await ctx.send(f"Currently Loaded Emojis: ({len(ctx.guild.emojis)} total) {''.join([str(i) for i in ctx.guild.emojis])}")

        else:
            await ctx.send(f"Emote `{name}` was not found in the database.")

    @commands.command()
    @commands.guild_only()
    async def listEmotes(self, ctx : commands.Context):
        '''
        Lists all emotes in the server, sent to DMs
        '''
        emotes = list(self.EMOTE_CACHE[ctx.guild.id].keys())

        break_lim = 30

        for i in range(0, len(emotes), break_lim): # break into chunks
            e = discord.Embed(title = "Custom Emotes for {} ({} to {})".format(ctx.guild.name, i+1, (i+1+break_lim if i+1+break_lim < len(emotes) else len(emotes))),
            colour=discord.Colour.from_rgb(*DBcfgitem(ctx.guild.id,"theme-colour")))
            
            for k in emotes[i:i + break_lim]: e.add_field(name=k, value="[Link]({})".format(self.EMOTE_CACHE[ctx.guild.id][k]))
            
            await DM(s="", user=ctx.author, embed=e)
        await delSend(ctx, "Check your DMs {}".format(ctx.author.mention))

    @commands.command()
    @commands.guild_only()
    @commands.check(isOP)
    async def removeEmote(self, ctx: commands.Context, name):
        '''
        Removes a custom emote from the Comrade Emote System
        '''
        if name.lower() in self.EMOTE_CACHE[ctx.guild.id]:
            async for m in (await getChannel(ctx.guild, 'emote-directory')).history(limit = None):
                if name.lower() in m.content:
                    await m.delete()
                    del self.EMOTE_CACHE[ctx.guild.id][name.lower()]
                    continue
            await ctx.send("Emote `{}` was removed.".format(name.lower()))
        else:
            await ctx.send("Emote `{}` was not found.".format(name.lower()))

    @commands.command()
    @commands.guild_only()
    @commands.check(isOP)
    async def renameEmote(self, ctx: commands.Context, name_old, name_new):
        '''
        Renames an emote in the emote system by removing and re-adding it
        '''
        try:
            url = self.EMOTE_CACHE[ctx.guild.id][name_old]
            await self.removeEmote(ctx, name_old)
            await self.addEmote(ctx, name_new, url)

        except:
            await ctx.send(f"Emote `{name_old}` was not found.")

    @commands.command()
    @commands.guild_only()
    async def emote(self, ctx : commands.Context, e:str):
        '''
        Sends an emote into a context, injecting first if necessary
        '''

        # Stage 1: Search server cache

        if emote := discord.utils.get(ctx.guild.emojis, name=e): await ctx.send(emote)
        
        # Stage 2: Search MongoDB
        elif document := DBcollection("Emotes").find_one({"name":e, "server":ctx.guild.id}):

            # 2A: inline emoji, needs to be added            
            if document["type"] == "inline": 
                await self.inject(ctx, e)

                await self.emote(ctx, e) # emoji is now loaded, should be able to call directly.
                # FUTURE: replace with Echo

            # 2B: Big emoji, send as-is
            elif document["type"] == "big":
                f = discord.File(fp=io.BytesIO(document["file"]), filename="image.png")
                await ctx.send(file=f)
        else:
            await ctx.send(f"Emote `{e}` not found.")

        # except:
        #     await reactX(ctx)
        #     similar = [i for i in self.EMOTE_CACHE[ctx.guild.id] if fuzz.partial_ratio(i, e) > 60]

        #     embed = discord.Embed(description="Emote `{}` not found. Did you mean one of the following?".format(e))

        #     if similar != []:
        #         for k in similar: embed.add_field(name="Suggestion", value=":{}:".format(k))
        #     else:
        #         directory = await getChannel(ctx.guild, 'emote-directory')
        #         embed.add_field(name="Sorry, no similar results were found.", value="See {}, or type `{}listemotes` for a list of all emotes.".format(directory.mention, BOT_PREFIX))

        #     await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        '''
        Emote listener
        '''
        if message.content and not message.author.bot and message.guild and message.content[0] == ':' and message.content[-1] == ':' and len(message.content) > 1:
            await self.emote(await self.bot.get_context(message), message.content.strip(':').strip(" "))

            
                    


            
    