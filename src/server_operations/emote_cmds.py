import discord
from discord.ext import commands
from utils import *

import re, requests, bson, io, imghdr, asyncio, os
from fuzzywuzzy import fuzz # NOTE: install python-Levenshtein for faster results.

from utils.checks.other_checks import match_url

from google.cloud import storage
from google.oauth2 import credentials, service_account

from PIL import Image

with open("temp.json", "w") as f: f.write(os.environ.get('GC'))

storage_client = storage.Client.from_service_account_json("temp.json")

os.remove("temp.json")

bucket = storage_client.get_bucket('comrade_emotes')

print("Connection to Google Cloud Storage Successful.")


class Emotes(commands.Cog):
    '''
    Use :emotename: to call an emote
    Use /emotename/ to swap its type

    Emotes exist as 1) Inline Discord Emoji and 2) Big Images
    Keep wide images as big emotes, and use small square ones as inline emotes.
    
    CES - Comrade Emote System v3.0
    Developed by itchono and Slyflare
    With testing from the rest of the Comrade team
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

        # make sure it doesn't already exist
        if not DBcollection(EMOTES_COL).find_one({"name":name, "server":ctx.guild.id}):
    
            await self.upload(ctx, name, url, "big") # upload as big by default
            
            await ctx.send(f'Emote `{name}` was added. you can call it using `:{name}:`')
        
        else:
            await reactX(ctx)
            await ctx.send(f'Emote `{name}` already exists! Contact a mod to get this fixed.')


    async def upload(self, ctx, name, url, emote_type):
        '''
        Uploads an emote into CES provided a name and a url.
        '''
        content = requests.get(url).content

        ext = imghdr.what(None, h=content) # determine the file extension

        imgfile = io.BytesIO(content)

        blob = storage.Blob(f"{ctx.guild.id}{name}.{ext}", bucket)

        if emote_type == "big" and ext in ["jpeg", "png", "jpg"]:
            img = Image.open(imgfile)

            aspect = img.size[0]/img.size[1]

            if img.size[0] > 1000:
                img.resize((1000, round(1000/aspect)), Image.ANTIALIAS)

            elif img.size[1] > 1000:
                img.resize((round(1000*aspect), 1000), Image.ANTIALIAS)

            imgfile = io.BytesIO()
            img.save(imgfile, optimize=True, format=ext, quality=65)
            imgfile.seek(0)

        # file-like representation of the attachment
        blob.upload_from_file(imgfile) # Upload to Google Cloud

        DBcollection(EMOTES_COL).insert_one(
            {"name":name,
            "server":ctx.guild.id,
            "type":emote_type,
            "ext":ext,
            "URL":blob.media_link})

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
                    
                    await self.upload(ctx, unload.name, unload.url, "inline") # upload the about-to-be-destroyed emoji

                await unload.delete(reason=f"Unloading emoji to make space for {name}")

            ## LOAD NEW EMOJI
            return await ctx.guild.create_custom_emoji(name=document["name"], image=requests.get(document["URL"]).content, reason=f"Requested by user {ctx.author.display_name}")
            
        else: await ctx.send(f"Emote `{name}` was not found in the database.")


    @commands.command()
    @commands.guild_only()
    async def listBig(self, ctx : commands.Context, page=1):
        '''
        Lists all big emotes in the server, based on page
        '''
        paginator = commands.Paginator(prefix="", suffix="", max_size=200)

        bigemotes = DBcollection(EMOTES_COL).find({"server":ctx.guild.id, "type":"big"}, {"name":True})

        for i in bigemotes:
            paginator.add_line(f"- {i['name']}")

        pagenum = 1

        pages = paginator.pages

        m = await ctx.send(f"__**Big Emotes in {ctx.guild.name} ({pagenum}/{len(pages)})**__:{pages[pagenum-1]}")

        cont = True

        for r in ["⬅", "➡", "🗑️"]: await m.add_reaction(r)

        def check(reaction, user):
            return str(reaction) in ["⬅", "➡", "🗑️"] and user == ctx.author and reaction.message.id == m.id

        while cont:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=180)

                await m.remove_reaction(reaction, user)
                if str(reaction) == "⬅" and pagenum > 1:
                    pagenum -= 1
                    await m.edit(content=f"__**Big Emotes in {ctx.guild.name} ({pagenum}/{len(pages)})**__:{pages[pagenum-1]}") 
                elif str(reaction) == "➡" and pagenum < len(pages):
                    pagenum += 1
                    await m.edit(content=f"__**Big Emotes in {ctx.guild.name} ({pagenum}/{len(pages)})**__:{pages[pagenum-1]}") 
                elif str(reaction) == "🗑️":
                    await m.delete()
                    cont = False
                    continue

            except asyncio.TimeoutError:
                cont = False
                continue

    @commands.command()
    @commands.guild_only()
    async def listInline(self, ctx : commands.Context, page=1):
        '''
        Lists all inline emotes in the server, based on page.
        NOTE: this may not include all inline emoji, especially if the bot was recently added to the server.
        '''
        paginator = commands.Paginator(prefix="", suffix="", max_size=200)

        inlineemotes = DBcollection(EMOTES_COL).find({"server":ctx.guild.id, "type":"inline"}, {"name":True})

        for i in inlineemotes:
            paginator.add_line(f"- {i['name']}")

        pagenum = 1

        pages = paginator.pages

        m = await ctx.send(f"__**Inline Emotes in {ctx.guild.name} ({pagenum}/{len(pages)})**__:{pages[pagenum-1]}")

        cont = True

        for r in ["⬅", "➡", "🗑️"]: await m.add_reaction(r)

        def check(reaction, user):
            return str(reaction) in ["⬅", "➡", "🗑️"] and user == ctx.author and reaction.message.id == m.id

        while cont:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=180)

                await m.remove_reaction(reaction, user)
                if str(reaction) == "⬅" and pagenum > 1:
                    pagenum -= 1
                    await m.edit(content=f"__**Inline Emotes in {ctx.guild.name} ({pagenum}/{len(pages)})**__:{pages[pagenum-1]}") 
                elif str(reaction) == "➡" and pagenum < len(pages):
                    pagenum += 1
                    await m.edit(content=f"__**Inline Emotes in {ctx.guild.name} ({pagenum}/{len(pages)})**__:{pages[pagenum-1]}") 
                elif str(reaction) == "🗑️":
                    await m.delete()
                    cont = False
                    continue

            except asyncio.TimeoutError:
                cont = False
                continue

    @commands.command()
    @commands.guild_only()
    @commands.check(isOP)
    async def removeEmote(self, ctx: commands.Context, name):
        '''
        Removes a custom emote from the Comrade Emote System
        '''
        if e := DBcollection(EMOTES_COL).find_one({"name":name, "server":ctx.guild.id}):

            try:
                blob = storage.Blob(f"{ctx.guild.id}{name}.{e['ext']}", bucket)
                blob.delete()
            except: pass

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
            # in mongodb already; most routine change

            newtype = {"big":"inline", "inline":"big"}[document["type"]]

            if document["type"] == "inline":
                emote = discord.utils.get(ctx.guild.emojis, name=document['name'])
                try: await emote.delete(reason=f"Unloading emoji because it changed type.")
                except: pass
            
            elif (size := len(requests.get(document["URL"]).content)) >= 262143:
                await ctx.send(f"Emote `{document['name']}` is too big to become inline! ({round(size/1024)} kb vs 256 kb limit)"); return
            
            else: await self.inject(ctx, document['name']) # inject the emote

            DBcollection(EMOTES_COL).update_one({"name":document['name'], "server":ctx.guild.id}, {"$set": {"type":newtype}})

            await ctx.send(f"Emote `{document['name']}` is now of type `{newtype}`")

        elif emote := discord.utils.get(ctx.guild.emojis, name=name):
            # in server, and not on mongodb (fringe case)
            await self.upload(ctx, name, emote.url, "big")
            try: await emote.delete(reason=f"Unloading emoji because it changed type.")
            except: pass

            await ctx.send(f"Emote `{name}` is now of type `big` (newly uploaded)")

        else: 
            # not in mongodb or in server
            
            await ctx.send(f"Emote `{name}` was not found.")

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
                eb = discord.Embed()
                eb.set_image(url=document["URL"])
                if len(e) > 32: e = e[:32]
                await mimic(ctx.channel, embed=eb, avatar_url=ctx.author.avatar_url, username=e)
        
        else:
            bigemotes = DBcollection(EMOTES_COL).find({"server":ctx.guild.id, "type":"big"}, {"name":True})

            similar = [i["name"] for i in bigemotes if fuzz.partial_ratio(i["name"], e) > 60]

            embed = discord.Embed(description=f"Emote `{e}` not found. Did you mean one of the following?")

            for k in similar: embed.add_field(name="Suggestion", value=":{}:".format(k))

            await ctx.send(embed=embed)

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
                    "g":"b##\n#bb\n#b#\n#b#\nb##",
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
                if len(out) > 2000:
                    await ctx.send(f"Text is too long! ({len(out)} vs 2000 char limit)")
                else: await ctx.send(out)
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

            servercfg = DBfind_one(SERVERCFG_COL, {"_id":message.guild.id})


            if re.match(r"^:.*:$", message.content) and (s := await pullemote(message.content)):
                await echo(await self.bot.get_context(message), member=message.author, content=s, file=await message.attachments[0].to_file() if message.attachments else None, embed=message.embeds[0] if message.embeds else None)
                await message.delete()

            elif match := re.findall(r"(?<!\<):.[^<>:]*:", message.clean_content) and "bypass-emotes" in servercfg and not servercfg["bypass-emotes"]:
                s = message.content
                send = False
                for i in match:
                    if emote := await pullemote(i): send = True; s = s.replace(i, str(emote))
                    else: await self.emote(await self.bot.get_context(message), i.strip(":").strip(" "))
                
                # if send:
                #     await echo(await self.bot.get_context(message), member=message.author, content=s, 
                #     file=await message.attachments[0].to_file() if message.attachments else None, embed=message.embeds[0] if message.embeds else None)

                #     await message.delete()
                # TODO fix

            elif message.content[0] == '/' and message.content[-1] == '/' and len(message.content) > 1:
                await self.swaptype(await self.bot.get_context(message), message.content.strip('/').strip(" ")) # Swap type of emote

            
    # @commands.command()
    # @commands.check_any(commands.is_owner(), isServerOwner())
    # async def migrate(self, ctx:commands.Context):
    #     '''
    #     Migrates mongodb emotes to GCS
    #     '''
    #     await ctx.send("Migration in progress. Please wait.")

    #     for document in DBcollection(EMOTES_COL).find({"server":ctx.guild.id}):
            
    #         DBcollection(EMOTES_COL).delete_one({"_id":document["_id"]})
            
    #         cop = document.copy()
            
    #         content = cop["file"] # bytes data

    #         ext = imghdr.what(None, h=content) # determine the file extension

    #         blob = storage.Blob(f"{ctx.guild.id}{cop['name']}.{ext}", bucket)

    #         # file-like representation of the attachment
    #         blob.upload_from_file(io.BytesIO(content)) # Upload to Google Cloud

    #         DBcollection(EMOTES_COL).insert_one(
    #             {"name":cop["name"],
    #             "server":ctx.guild.id,
    #             "type":cop["type"],
    #             "ext":ext,
    #             "URL":blob.media_link})      

    #     await ctx.send("Migration complete.")    
    
    # @commands.command()
    # @commands.check_any(commands.is_owner(), isServerOwner())
    # async def ingestfromchannel(self, ctx:commands.Context, channel:discord.TextChannel):
    #     '''
    #     ingests emotes from channel
    #     '''
    #     async for e in channel.history(limit=None):
    #         try: 
    #             name = e.content.lower().split("\n")[0]

    #             url = e.content.split("\n")[1]

    #             await self.addEmote(ctx, name, url=url)
                
    #         except: pass # dirty emote directory