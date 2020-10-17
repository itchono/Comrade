import discord
from discord.ext import commands
from utils import *

import re, requests, bson, io, imghdr
from fuzzywuzzy import fuzz # NOTE: install python-Levenshtein for faster results.

from utils.checks.other_checks import match_url

class Emotes(commands.Cog):
    '''
    Use :emotename: to call an emote
    Use /emotename/ to swap its type

    Emotes exist as 1) Inline Discord Emoji and 2) Big Images
    Keep wide images as big emotes, and use small square ones as inline emotes.
    
    CES - Comrade Emote System
    Developed by itchono and Slyflare
    '''
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def addEmote(self, ctx: commands.Context, name, url=None):
        '''
        Adds a custom emote to the Comrade Emote System. Adds as a big emote by default.
        '''
        try:
            if not url: url = ctx.message.attachments[0].url
        except:
            if not match_url(url): await ctx.send("Invalid URL Provided."); return

        if not DBcollection(EMOTES_COL).find_one({"name":name, "server":ctx.guild.id}):
            # make sure it doesn't already exist

            binImage = requests.get(url).content # binaries

            DBcollection(EMOTES_COL).insert_one(
                {"name":name,
                "server":ctx.guild.id,
                "type":"big",
                "file":binImage})
            
            await ctx.send(f'Emote `{name}` was added. you can call it using `:{name}:`')
        
        else:
            await reactX(ctx)
            await ctx.send(f'Emote `{name}` already exists! Contact a mod to get this fixed.')


    async def inject(self, ctx:commands.Context, name):
        '''
        Attempts to inject image into the server's list of emoji, returning it afterward
        '''

        if document := DBcollection(EMOTES_COL).find_one({"name": name, "server":ctx.guild.id}):
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

             ## binary data
            data = document["file"]
            ## LOAD NEW EMOJI
            return await ctx.guild.create_custom_emoji(name=document["name"], image=data, reason=f"Requested by user {ctx.author.display_name}")
            
        else: await ctx.send(f"Emote `{name}` was not found in the database.")

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


        # emotes = list(self.EMOTE_CACHdocument[ctx.guild.id].keys())

        # break_lim = 30

        # for i in range(0, len(emotes), break_lim): # break into chunks
        #     e = discord.Embed(title = "Custom Emotes for {} ({} to {})".format(ctx.guild.name, i+1, (i+1+break_lim if i+1+break_lim < len(emotes) else len(emotes))),
        #     colour=discord.Colour.from_rgb(*DBcfgitem(ctx.guild.id,"theme-colour")))
            
        #     for k in emotes[i:i + break_lim]: e.add_field(name=k, value="[Link]({})".format(self.EMOTE_CACHdocument[ctx.guild.id][k]))
            
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

        else: await ctx.send(f"Emote `{name}` was not found.")

    @commands.command()
    @commands.guild_only()
    @commands.check(isOP)
    async def renameEmote(self, ctx: commands.Context, name_old, name_new):
        '''
        Renames an emote in the emote system
        '''
        if DBcollection(EMOTES_COL).update_one({"name":name_old, "server":ctx.guild.id}, {"$set":{"name":name_new}}):
            await ctx.send(f"Emote `{name_old}` was renamed.")
        else: await ctx.send(f"Emote `{name_old}` was not found.")

    @commands.command()
    @commands.guild_only()
    async def swaptype(self, ctx: commands.Context, name):
        '''
        Swaps the type of the emote
        '''
        if (document := DBcollection(EMOTES_COL).find_one({"name": name, "server":ctx.guild.id})) or \
            (document := DBcollection(EMOTES_COL).find_one({"name": re.compile('^' + name + '$', re.IGNORECASE), "server":ctx.guild.id})):
            newtype = {"big":"inline", "inline":"big"}[document["type"]]

            if document["type"] == "inline":
                emote = discord.utils.get(ctx.guild.emojis, name=document['name'])
                try: await emote.delete(reason=f"Unloading emoji because it changed type.")
                except: pass
            
            elif (size := len(document["file"])) >= 262143:
                await ctx.send(f"Emote `{document['name']}` is too big to become inline! ({round(size/1024)} kb vs 256 kb limit)"); return

            DBcollection(EMOTES_COL).update_one({"name":document['name'], "server":ctx.guild.id}, {"$set": {"type":newtype}})

            await ctx.send(f"Emote `{document['name']}` is now of type `{newtype}`")

        else: await ctx.send(f"Emote `{name}` was not found.")


    async def inline(self, ctx: commands.Context, e:str):
        '''
        Gets an inline emote from Discord, if it exists, else it injects it and returns it
        Similar code to emote function
        '''
        # Stage 1: Search server cache
        if emote := discord.utils.get(ctx.guild.emojis, name=e): return emote

        # Stage 2: Search MongoDB
        elif ((document := DBcollection(EMOTES_COL).find_one({"name": e, "server":ctx.guild.id})) or \
            (document := DBcollection(EMOTES_COL).find_one({"name": re.compile('^' + e + '$', re.IGNORECASE), "server":ctx.guild.id}))) and \
            document["type"] == "inline":

            # maybe they just can't spell
            if emote := discord.utils.get(ctx.guild.emojis, name=document["name"]): return emote
            return await self.inject(ctx, document["name"])
        return None

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
        elif (document := DBcollection(EMOTES_COL).find_one({"name": e, "server":ctx.guild.id})) or \
            (document := DBcollection(EMOTES_COL).find_one({"name": re.compile('^' + e + '$', re.IGNORECASE), "server":ctx.guild.id})):

            # 2A: inline emoji, 
            # maybe they just can't spell
            if emote := discord.utils.get(ctx.guild.emojis, name=document["name"]):
                await echo(ctx, member=ctx.author, content=emote)
                await ctx.message.delete() # try to delete

            # Or, it needs to be added            
            if document["type"] == "inline": 
                emote = await self.inject(ctx, document["name"])
                await echo(ctx, member=ctx.author, content=emote)
                await ctx.message.delete() # try to delete

            # 2B: Big emoji, send as-is
            elif document["type"] == "big":
                byts = io.BytesIO(document["file"])
                ext = imghdr.what(None, h=byts.read()) # deteremine the file extension
                f = discord.File(fp=io.BytesIO(document["file"]), filename=f"image.{ext}")
                await mimic(ctx.channel, file=f, avatar_url=ctx.author.avatar_url, username=e)
        else:
            await ctx.send(f"Emote `{e}` not found.")

            '''
            TODO Implement similar emoji
            similar = [i for i in self.EMOTE_CACHdocument[ctx.guild.id] if fuzz.partial_ratio(i, e) > 60]

            embed = discord.Embed(description="Emote `{}` not found. Did you mean one of the following?".format(e))

            if similar != []:
                for k in similar: embed.add_field(name="Suggestion", value=":{}:".format(k))
            else:
                directory = await getChannel(ctx.guild, 'emote-directory')
                embed.add_field(name="Sorry, no similar results were found.", value="See {}, or type `{}listemotes` for a list of all emotes.".format(directory.mention, BOT_PREFIX))

            await ctx.send(embed=embed)
            ''' 

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

    @commands.command()
    async def ascii(self, ctx:commands.Context, name, *, text):
        '''
        Sends a big form of the emote in word art form
        '''

        letters = {"a":"###\n#b#\n###\n#b#\n#b#",
                    "b":"##b\n#b#\n###\n#b#\n##b",
                    "c":"###\n#bb\n#bb\n#bb\n###",
                    "d":"##b\n#b#\n#b#\n#b#\n##b",
                    "e":"###\n#bb\n###\n#bb\n###",
                    "f":"###\n#bb\n###\n#bb\n#bb",
                    "g":"###\n#bb\n###\n#b#\nb#b",
                    "h":"#b#\n#b#\n###\n#b#\n#b#",
                    "i":"###\nb#b\nb#b\nb#b\n###",
                    "j":"###\nb#b\nb#b\nb#b\n#bb",
                    "k":"#bb\n#bb\n#b#\n##b\n#b#",
                    "l":"#bb\n#bb\n#bb\n#bb\n###",
                    "m":"#b#\n###\n###\n#b#\n#b#",
                    "n":"bbb\nbbb\n##b\n#b#\n#b#",
                    "o":"###\n#b#\n#b#\n#b#\n###",
                    "p":"###\n#b#\n###\n#bb\n#bb",
                    "q":"b#b\n#b#\n#b#\nb##\nbb#",
                    "r":"##b\n#b#\n##b\n#b#\n#b#",
                    "s":"###\n#bb\n###\nbb#\n###",
                    "t":"###\nb#b\nb#b\nb#b\nb#b",
                    "u":"#b#\n#b#\n#b#\n#b#\n###",
                    "v":"#b#\n#b#\n#b#\n#b#\nb#b",
                    "w":"#b#\n#b#\n###\n###\n#b#",
                    "x":"#b#\n#b#\nb#b\n#b#\n#b#",
                    "y":"#b#\n#b#\nb#b\nb#b\nb#b",
                    "z":"###\nbb#\nb#b\n#bb\n###"}
        if text.isalpha():

            if emote := await self.inline(ctx, name):
                out = ""
                for c in text.lower():
                    ch = letters[c].replace("b",":black_small_square:").replace("#",str(emote))
                    out += ch + "\n\n"
                await ctx.send(out)
            else:
                await ctx.send("Emote not found.")
        else:
            await ctx.send("Text must be alphabetical only.")
        
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        '''
        Emote listener
        '''
        async def pullemote(em):
            return await self.inline(await self.bot.get_context(message), em.strip(':').strip(" "))

        if message.content and not message.author.bot and message.guild: 

            if match := re.findall(r"(?<!\<):.[^<>:]*:", message.clean_content):
                s = message.content
                send = False
                for i in match:
                    if emote := await pullemote(i): send = True; s = s.replace(i, str(emote))
                    else: await self.emote(await self.bot.get_context(message), i.strip(":").strip(" "))
                
                if send:
                    await echo(await self.bot.get_context(message), member=message.author, content=s, 
                    file=await message.attachments[0].to_file() if message.attachments else None, embed=message.embeds[0] if message.embeds else None)

                    await message.delete()

            elif message.content[0] == '/' and message.content[-1] == '/' and len(message.content) > 1:
                await self.swaptype(await self.bot.get_context(message), message.content.strip('/').strip(" ")) # Swap type of emote

            
                    


            
    