'''
Emotes exist as 1) Inline Discord Emoji and 2) Big Images
Keep wide images as big emotes, and use small square ones as inline emotes.

CES - Comrade Emote System v5.0
Developed by itchono and Slyflare
With testing from the rest of the Comrade team
'''
import discord
from discord.ext import commands

import imghdr
import re
import io
import aiohttp
from PIL import Image
from typing import Optional, Union

from discord.partial_emoji import PartialEmoji

from db import collection, emote_channel
from utils.utilities import is_url, bot_prefix
from utils.reactions import reactX
from utils.echo import echo, mimic
from utils.checks import isOP
from utils.button_menu import send_menu

session = aiohttp.ClientSession()


# Custom emoji converter class
class ComradeEmojiConverter(commands.Converter):
    '''
    Finds emoji based on Comrade system or otherwise.

    Parameters
    ----------
    emote: str
        name, discord formatted emoji, etc..

    Returns
    -------
    discord.Emoji: animated or regular emoji
    discord.PartialEmoji: unicode emoji
    dict: Comrade custom large emoji {name, URL}
    '''
    async def convert(self, ctx: commands.Context,
                      emote: str) -> \
            Union[discord.Emoji, dict, str]:
        # Stage 1: Try direct conversion
        try:
            emoji = await commands.EmojiConverter().convert(ctx, emote)
            if emoji.guild == ctx.guild:
                return emoji
            else:
                raise Exception(f"Emoji is not in this server.")
        except BaseException:
            pass

        # Stage 2: Search MongoDB
        if (document := collection("emotes").find_one(
            {"name": emote, "server": ctx.guild.id})) or \
                (document := collection("emotes").find_one(
                    {"name": re.compile('^' + emote + '$', re.IGNORECASE),
                        "server": ctx.guild.id})):

            # 2A: inline emoji,
            # maybe they just got the case wrong
            if emote := discord.utils.get(
                    ctx.guild.emojis, name=document["name"]):
                return emote

            # Or, it needs to be added
            elif document["type"] == "inline":
                return await inject(ctx, document["name"])

            # 2B: Big emoji, send as-is
            elif document["type"] == "big":
                return document

        # Stage 3: Unicode Emoji
        try:
            emoji = PartialEmoji(name=emote)
            if emoji.is_unicode_emoji():
                return emoji
            return None
        except commands.BadArgument:
            return None
        # ISSUE: does not check if emoji is valid unicode emoji.


async def upload(ctx, name, url, emote_type="auto") -> str:
    '''
    Uploads an emote into CES provided a name and a url.
    '''
    async with session.get(url) as resp:
        content = await resp.read()

    ext = imghdr.what(None, h=content)
    # determine the file extension

    content = io.BytesIO(content)

    channel = emote_channel(ctx.guild)

    if ext is None:
        raise TypeError(
            "Could not download emote. Check that you are actually linking to an image or GIF.")

    if emote_type == "auto":
        # Automatically make inline
        im = Image.open(content)

        content.seek(0)

        emote_type = "inline" if max(im.size) < 256 else "big"

    msg = await channel.send(
        file=discord.File(content, filename=f"{name}.{ext}"))

    collection("emotes").insert_one(
        {"name": name,
         "server": ctx.guild.id,
         "type": emote_type,
         "ext": ext,
         "URL": str(msg.attachments[0].url),
         "size": msg.attachments[0].size})

    return emote_type


async def inject(ctx: commands.Context, name) -> discord.Emoji:
    '''
    Attempts to inject image into the server's list of emoji,
    returning it afterward
    '''
    if document := collection("emotes").find_one(
            {"name": name, "server": ctx.guild.id}):
        LIMIT = 50

        # UNLOAD EMOJI
        if len(ctx.guild.emojis) >= LIMIT - 1:

            unload = ctx.guild.emojis[0]  # emoji to be unloaded -- oldest one

            if not collection("emotes").find_one(
                    {"name": unload.name, "server": ctx.guild.id}):
                # If not loaded, we must first database it

                # upload the about-to-be-destroyed emoji
                await upload(ctx, unload.name, str(unload.url), "inline")

            await unload.delete(reason=f"Unloading emoji to make space for {name}")

        # LOAD NEW EMOJI
        async with session.get(document["URL"]) as resp:
            content = await resp.read()

            # March 7: Fix by Sean to handle webp images
            if document["URL"].endswith("webp"):
                im = Image.open(io.BytesIO(content))
                content = io.BytesIO()
                im.save(content, format='png')
                content = content.getvalue()

        return await ctx.guild.create_custom_emoji(name=document["name"], image=content, reason=f"Requested by user {ctx.author.display_name}")

    else:
        await ctx.send(f"Emote `{name}` was not found in the database.")
        return None


class Emotes(commands.Cog):
    '''
    Custom Emote System.
    `:emotename:` call
    `\emotename\` swap type
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def emote(self, ctx: commands.Context, e: str):
        '''
        Sends an emote into a context, injecting first if necessary

        Subcommands: add, remove, rename
        '''
        if ctx.invoked_subcommand is None:

            emote = await ComradeEmojiConverter().convert(ctx, e)

            if type(emote) is discord.Emoji:
                # Inline emoji
                await echo(ctx, member=ctx.author, content=emote)

            elif type(emote) is dict:
                # Big emote
                eb = discord.Embed()
                eb.set_image(url=emote["URL"])
                await mimic(ctx.channel,
                            embed=eb,
                            avatar_url=ctx.author.avatar_url,
                            username=emote["name"])

    @emote.command()
    @commands.guild_only()
    async def add(self, ctx: commands.Context, name: str, url=None):
        '''
        Adds a custom emote to the Comrade Emote System.
        Adds as a big emote by default.
        '''
        try:
            if not url:
                url = str(ctx.message.attachments[0].url)
        except BaseException:
            if not is_url(url):
                await ctx.send("Invalid URL Provided.")
                return

        # Validate Name
        if not re.match(r'^\w+$', name):
            await ctx.send("Name must only consist of letters, numbers, and underscores.")
            return
        elif len(name) > 32 or len(name) < 2:
            await ctx.send("Name must be 2 to 32 chars long")
            return

        # make sure it doesn't already exist
        if not collection("emotes").find_one(
                {"name": name, "server": ctx.guild.id}):
            await ctx.trigger_typing()

            # upload as big by default
            type = await upload(ctx, name, url)

            if type == "inline":
                emote = await inject(ctx, name)
                await ctx.send(f'Emote `{name}` was added.'
                            f'You can call {emote} using `:{name}:`')
            else:
                await ctx.send(f'Emote `{name}` was added. '
                            f'You can call it using `:{name}:`')

        else:
            await reactX(ctx)
            await ctx.send(f'Emote `{name}` already exists! '
                           'Contact a mod to get this fixed.')

    @commands.command()
    @commands.guild_only()
    async def addemote(self, ctx: commands.Context, name: str, url=None):
        '''
        Alias for emote add
        '''
        await self.add(ctx, name, url)

    @commands.command()
    @commands.guild_only()
    async def copyemote(self, ctx: commands.Context, emote: discord.PartialEmoji, name: Optional[str] = None):
        '''
        Alias for emote copy
        '''
        await self.copy(ctx, emote, name)

    @emote.command()
    @commands.guild_only()
    async def copy(self, ctx: commands.Context, emote: discord.PartialEmoji,
                   name: Optional[str] = None):
        '''
        Copies emoji from another context into this server, optionally specifying a different name.
        You can type the emoji directly if you have nitro, or paste its ID.
        '''
        if not name:
            name = emote.name

        if emote.animated:
            await self.add(ctx, name, f"https://cdn.discordapp.com/emojis/{emote.id}.gif?v=1")
        else:
            await self.add(ctx, name, f"https://cdn.discordapp.com/emojis/{emote.id}.png?v=1")

    @emote.command()
    @commands.guild_only()
    async def steal(self, ctx: commands.Context, name: Optional[str] = None):
        '''
        Steals emoji from the message you reply to.
        Use this instead of `copy` if you're non-nitro
        '''
        if ref := ctx.message.reference:
            msg = await ctx.fetch_message(ref.message_id)

            em = await commands.PartialEmojiConverter().convert(ctx, msg.content)

            await self.copy(ctx, em, name)

    @commands.command()
    @commands.guild_only()
    async def addemojigg(self, ctx: commands.Context, name: str):
        '''
        Add emote from emoji.gg

        Should be of form ####-name
        eg. 5492_EzPepe
        '''

        url = f"https://emoji.gg/assets/emoji/{name}.png"

        async with session.get(url) as resp:
            if resp.status == 404:
                url = f"https://emoji.gg/assets/emoji/{name}.gif"
                async with session.get(url) as resp:
                    if resp.status == 404:
                        await ctx.send("Invalid name. Valid Example: `$c addemojigg 5492_EzPepe`")

        name = name.split("_")[1]

        await self.add(ctx, name, url)

    @emote.command()
    @commands.check(isOP())
    @commands.guild_only()
    async def remove(self, ctx: commands.Context, name):
        '''
        Removes a custom emote from the Comrade Emote System
        '''
        if e := collection("emotes").find_one(
                {"name": name, "server": ctx.guild.id}):

            collection("emotes").delete_one(
                {"name": name, "server": ctx.guild.id})
            await ctx.send(f"Emote `{name}` was removed.")

            if e["type"] == "inline":
                emote = discord.utils.get(ctx.guild.emojis, name=name)
                try:
                    await emote.delete(reason="Unloading emoji because "
                                       "it was removed from the server.")
                except BaseException:
                    pass
        else:
            await ctx.send(f"Emote `{name}` was not found.")

    @emote.command()
    @commands.guild_only()
    async def rename(self, ctx: commands.Context, name_old, name_new):
        '''
        Renames an emote in the emote system
        '''
        if collection("emotes").update_one(
                {"name": name_old, "server": ctx.guild.id},
                {"$set": {"name": name_new}}):
            await ctx.send(f"Emote `{name_old}` was renamed.")

            if e := collection("emotes").find_one(
                {"name": name_old, "server": ctx.guild.id}):

                if e["type"] == "inline":
                    emote = discord.utils.get(ctx.guild.emojis, name=name_old)
                    try:
                        await emote.edit(name = name_new)
                    except BaseException:
                        pass
        else:
            await ctx.send(f"Emote `{name_old}` was not found.")

    @emote.command()
    @commands.guild_only()
    async def gallery(self, ctx: commands.Context, start_position: int = 1):
        '''
        Gallery of all big emotes in server
        Can specify starting position to skip ahead
        '''
        bigemotes = collection("emotes").find(
            {"server": ctx.guild.id, "type": "big"}).sort(
                "name", 1)

        if not bigemotes:
            return  # empty
        bigemotes = list(bigemotes)

        def em_embed(pagenum):
            e = discord.Embed(color=0xd7342a)
            e.set_author(name=bigemotes[pagenum]["name"],
                         url=bigemotes[pagenum]["URL"])
            e.set_image(url=bigemotes[pagenum]["URL"])
            e.set_footer(text=f"{pagenum+1}/{len(bigemotes)}")
            return e

        await send_menu(ctx, [em_embed(num) for num in range(len(bigemotes))])

    @emote.group()
    @commands.guild_only()
    async def list(self, ctx: commands.Context):
        '''
        Sends a list of emotes by name.
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send(f"Run `{bot_prefix}emote list big` or "
                           f"`{bot_prefix}emote list inline` to see a list "
                           "or big and inline emotes respectively")

    @list.command()
    @commands.guild_only()
    async def big(self, ctx: commands.Context, page=1):
        '''
        Lists all big emotes in the server, based on page
        '''
        paginator = commands.Paginator(prefix="", suffix="", max_size=200)

        bigemotes = collection("emotes").find(
            {"server": ctx.guild.id, "type": "big"}, {"name": True}).sort(
                "name", 1)

        if not bigemotes:
            return  # empty

        for i in bigemotes:
            paginator.add_line(f"- {i['name']}")

        pages = paginator.pages

        def em_embed(pagenum):
            e = discord.Embed(color=0xd7342a, title=f"__**Big Emotes in {ctx.guild.name}**__")
            e.set_footer(text=f"({pagenum + 1}/{len(pages)})")
            e.description = pages[pagenum]
            return e

        await send_menu(ctx, [em_embed(num) for num in range(len(pages))])

    @list.command()
    @commands.guild_only()
    async def inline(self, ctx: commands.Context, page=1):
        '''
        Lists all inline emotes in the server, based on page.
        This may not include all inline emoji,
        especially if the bot was recently added to the server.
        '''
        paginator = commands.Paginator(prefix="", suffix="", max_size=200)

        inlineemotes = collection("emotes").find(
            {"server": ctx.guild.id, "type": "inline"}, {"name": True}).sort(
                "name", 1)

        if not inlineemotes:
            return  # empty

        for i in inlineemotes:
            if emote := discord.utils.find(lambda m: m.name == i['name'], ctx.guild.emojis):
                paginator.add_line(f"- {i['name']} {emote}")
            else:
                paginator.add_line(f"- {i['name']}")

        pages = paginator.pages

        def em_embed(pagenum):
            e = discord.Embed(color=0xd7342a, title=f"__**Inline Emotes in {ctx.guild.name}**__")
            e.set_footer(text=f"({pagenum + 1}/{len(pages)})")
            e.description = pages[pagenum]
            return e

        await send_menu(ctx, [em_embed(num) for num in range(len(pages))])

    @commands.command()
    @commands.guild_only()
    async def swaptype(self, ctx: commands.Context, name):
        '''
        Swaps the type of the emote
        '''
        if (document := collection("emotes").find_one({"name": name, "server": ctx.guild.id})) or (document := collection(
                "emotes").find_one({"name": re.compile('^' + name + '$', re.IGNORECASE), "server": ctx.guild.id})):
            # in mongodb already; most routine change

            newtype = {"big": "inline", "inline": "big"}[document["type"]]

            if document["type"] == "inline":
                emote = discord.utils.get(
                    ctx.guild.emojis, name=document['name'])
                try:
                    await emote.delete(reason=f"Unloading emoji because it changed type.")
                except BaseException:
                    pass

            elif (size := document["size"]) >= 262143:
                await ctx.send(f"Emote `{document['name']}` is too big to become inline! ({round(size/1024)} kb vs 256 kb limit)")
                return

            else:
                await inject(ctx, document['name'])  # inject the emote

            collection("emotes").update_one(
                {"name": document['name'], "server": ctx.guild.id}, {"$set": {"type": newtype}})

            await ctx.send(f"Emote `{document['name']}` is now of type `{newtype}`")

        elif emote := discord.utils.get(ctx.guild.emojis, name=name):
            # in server, and not on mongodb (fringe case)
            await upload(ctx, name, str(emote.url), "big")
            try:
                await emote.delete(reason=f"Unloading emoji because it changed type.")
            except BaseException:
                pass
            await ctx.send(f"Emote `{name}` is now of type `big` (newly uploaded)")

        else:
            # not in mongodb or in server
            await ctx.send(f"Emote `{name}` was not found.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        '''
        Emote listener
        '''
        async def pullemote(em):
            emote = await ComradeEmojiConverter().convert(
                await self.bot.get_context(message), em.strip(':').strip(" ")
            )
            if type(emote) is discord.Emoji:
                return emote
            return None

        if message.content and not message.author.bot and message.guild:

            # scan for inline emotes
            if match := re.findall(
                    r"(?<!<)(?<!a):\s*[0-9A-z]+\s*:(?!\d+>)",
                    message.clean_content):
                s = message.content
                send = False
                for i in match:
                    if emote := await pullemote(i):
                        send = True
                        s = s.replace(i, str(emote))
                    # else:
                    # Handled by Go Module

                if send:
                    await echo(await self.bot.get_context(message),
                               member=message.author, content=s,
                               file=await message.attachments[0].to_file()
                               if message.attachments else None,
                               embed=message.embeds[0]
                               if message.embeds else None)

                    await message.delete()

            # scan for changing emotes
            elif message.content[0] == '\\' and message.content[-1] == '\\' and \
                    len(message.content) > 1:
                # Swap type of emote
                await self.swaptype(
                    await self.bot.get_context(
                        message), message.content.strip('\\').strip(" "))
