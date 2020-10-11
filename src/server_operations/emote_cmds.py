import discord
from discord.ext import commands
from utils import *

import re, requests, bson, io, imghdr
from fuzzywuzzy import fuzz # NOTE: install python-Levenshtein for faster results.

from utils.checks.other_checks import match_url

class Emotes(commands.Cog):
    '''
    Developed by itchono and Slyflare
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

        if not DBcollection(EMOTES_COL).find_one({"name":name, "server":ctx.guild.id}):

            binImage = requests.get(url).content # binaries

            DBcollection(EMOTES_COL).insert_one(
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

        if not DBcollection(EMOTES_COL).find_one({"name":name.lower(), "server":ctx.guild.id}):
            # make sure it doesn't already exist

            binImage = requests.get(url).content # binaries

            DBcollection(EMOTES_COL).insert_one(
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

        if document := DBcollection(EMOTES_COL).find_one({"name": re.compile('^' + name + '$', re.IGNORECASE), "server":ctx.guild.id}):

            LIMIT = 50
            
            ## UNLOAD EMOJI
            if len(ctx.guild.emojis) >= LIMIT-1:

                unload = ctx.guild.emojis[0] # emoji to be unloaded -- oldest one

                if not DBcollection(EMOTES_COL).find_one({"name":unload.name, "server":ctx.guild.id}):
                    # If not loaded, we must first database it

                    binImage = requests.get(unload.url).content # binaries

                    DBcollection(EMOTES_COL).insert_one(
                        {"name":unload.name,
                        "server":ctx.guild.id,
                        "type":"inline",
                        "file":binImage})
                
                await unload.delete(reason=f"Unloading emoji to make space for {name}")

            ## LOAD NEW EMOJI
            data = document["file"]
            await ctx.guild.create_custom_emoji(name=name, image=data, reason=f"Requested by user {ctx.author.display_name}")
            ## binary data
            e = discord.utils.get(ctx.guild.emojis, name=name)

        else:
            await ctx.send(f"Emote `{name}` was not found in the database.")

    @commands.command()
    @commands.guild_only()
    async def listEmotes(self, ctx : commands.Context):
        '''
        Lists all emotes in the server, sent to DMs
        '''

        bigemotes = DBcollection(EMOTES_COL).find({"server":ctx.guild.id, "type":"big"}, {"name":True})

        bigs = "\n".join([i["name"] for i in bigemotes])

        inlineemotes = DBcollection(EMOTES_COL).find({"server":ctx.guild.id, "type":"inline"}, {"name":True})

        inlines = "\n".join([i["name"] for i in inlineemotes])

        await ctx.send(f"__Big__:\n{bigs}\n__Inlines__:\n{inlines}")


        # emotes = list(self.EMOTE_CACHE[ctx.guild.id].keys())

        # break_lim = 30

        # for i in range(0, len(emotes), break_lim): # break into chunks
        #     e = discord.Embed(title = "Custom Emotes for {} ({} to {})".format(ctx.guild.name, i+1, (i+1+break_lim if i+1+break_lim < len(emotes) else len(emotes))),
        #     colour=discord.Colour.from_rgb(*DBcfgitem(ctx.guild.id,"theme-colour")))
            
        #     for k in emotes[i:i + break_lim]: e.add_field(name=k, value="[Link]({})".format(self.EMOTE_CACHE[ctx.guild.id][k]))
            
        #     await DM(s="", user=ctx.author, embed=e)
        # await delSend(ctx, "Check your DMs {}".format(ctx.author.mention))

    @commands.command()
    @commands.guild_only()
    @commands.check(isOP)
    async def removeEmote(self, ctx: commands.Context, name):
        '''
        Removes a custom emote from the Comrade Emote System
        '''
        if e := DBcollection(EMOTES_COL).find_one({"name":name, "server":ctx.guild.id}):
            DBcollection(EMOTES_COL).delete_one({"name":name, "server":ctx.guild.id})
            await ctx.send(f"Emote `{name}` was removed.")

            if e["type"] == "inline":
                emote = discord.utils.get(ctx.guild.emojis, name=name)
                try: await emote.delete(reason=f"Unloading emoji because it was removed from the server.")
                except: pass

        else:
            await ctx.send(f"Emote `{name}` was not found.")

    @commands.command()
    @commands.guild_only()
    @commands.check(isOP)
    async def renameEmote(self, ctx: commands.Context, name_old, name_new):
        '''
        Renames an emote in the emote system
        '''
        if DBcollection(EMOTES_COL).update_one({"name":name_old, "server":ctx.guild.id}, {"$set":{"name":name_new}}):
            await ctx.send(f"Emote `{name_old}` was renamed.")
        else:
            await ctx.send(f"Emote `{name_old}` was not found.")

    @commands.command()
    @commands.guild_only()
    async def swaptype(self, ctx: commands.Context, name):
        '''
        Swaps the type of the emote
        '''
        if e := DBcollection(EMOTES_COL).find_one({"name": re.compile('^' + e + '$', re.IGNORECASE), "server":ctx.guild.id}):
            
            newtype = {"big":"inline", "inline":"big"}[e["type"]]

            if e["type"] == "inline":
                emote = discord.utils.get(ctx.guild.emojis, name=name)
                try: await emote.delete(reason=f"Unloading emoji because it changed type.")
                except: pass

            DBcollection(EMOTES_COL).update_one({"name":name, "server":ctx.guild.id}, {"$set": {"type":newtype} })

            await ctx.send(f"Emote `{name}` is now of type `{newtype}`")

        else:
            await ctx.send(f"Emote `{name}` was not found.")

    @commands.command()
    @commands.guild_only()
    async def emote(self, ctx : commands.Context, e:str):
        '''
        Sends an emote into a context, injecting first if necessary
        '''

        # Stage 1: Search server cache

        if emote := discord.utils.get(ctx.guild.emojis, name=e): 
            await echo(ctx, member=ctx.author, content=emote)
            await ctx.message.delete() # try to delete

        # Stage 2: Search MongoDB
        elif document := DBcollection(EMOTES_COL).find_one({"name": re.compile('^' + e + '$', re.IGNORECASE), "server":ctx.guild.id}):

            # 2A: inline emoji, needs to be added            
            if document["type"] == "inline": 
                await self.inject(ctx, e)

                # use emote
                if emote := discord.utils.get(ctx.guild.emojis, name=e): 
                    await echo(ctx, member=ctx.author, content=emote)
                    await ctx.message.delete() # try to delete

            # 2B: Big emoji, send as-is
            elif document["type"] == "big":
                byts = io.BytesIO(document["file"])
                ext = imghdr.what(None, h=byts.read())
                f = discord.File(fp=io.BytesIO(document["file"]), filename=f"image.{ext}")
                await mimic(ctx.channel, file=f, avatar_url=ctx.author.avatar_url, username=e)
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

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    async def ingestfromchannel(self, ctx:commands.Context, channel:discord.TextChannel):
        '''
        ingests emotes from channel
        '''

        async for e in channel.history(limit=None):
            try: 
                name = e.content.lower().split("\n")[0]

                url = e.content.split("\n")[1]

                await self.addEmote(ctx, name, url=url)
                
            except: pass # dirty emote directory
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        '''
        Emote listener
        '''
        if message.content and not message.author.bot and message.guild and message.content[0] == ':' and message.content[-1] == ':' and len(message.content) > 1:
            await self.emote(await self.bot.get_context(message), message.content.strip(':').strip(" "))

            
                    


            
    