# Abstractions for Comrade Emote System
from dis_snek.models.snek import InteractionContext
from dis_snek.models.discord import (CustomEmoji, PartialEmoji,
                                     File)
import re
import aiohttp
from io import BytesIO
from imghdr import what
from PIL import Image


class ComradeEmoji:
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
    @classmethod
    async def convert(cls, ctx: InteractionContext, emote_name: str) -> \
        CustomEmoji| PartialEmoji | dict | None:
            
        # Stage 1: Search local guild
        all_custom_emojis: list[CustomEmoji] = \
            await ctx.guild.get_all_custom_emojis()
        
        # See if any emojis match the name emote_name
        custom_emoji: CustomEmoji
        if custom_emoji := next(
            (e for e in all_custom_emojis if e.name == emote_name), None):
            return custom_emoji
    
        # Search mongodb for emoji
        collection = ctx.bot.db.Emotes
        
        # Stage 2: Search MongoDB
        if (document := collection.find_one(
            {"name": emote_name,
             "server": ctx.guild_id}))\
            or \
            (document := collection.find_one(
            {"name": re.compile('^' + emote_name + '$', re.IGNORECASE),
             "server": ctx.guild_id})):

            # 2A: inline emoji,
            # maybe they just got the case wrong
            if custom_emoji := next(
                (e for e in all_custom_emojis if
                 e.name == document["name"]), None):
                return custom_emoji

            # Or, it needs to be added
            elif document["type"] == "inline":
                return await inject(ctx, document["name"])

            # 2B: Big emoji, send as-is
            elif document["type"] == "big":
                return document

        # Stage 3: Unicode Emoji
        if len(emote_name) == 1:
            return PartialEmoji.from_str(emote_name)
        # ISSUE: does not check if emoji is valid unicode emoji.
        return None


async def upload(ctx, name, url, emote_type="auto") -> str:
    '''
    Uploads an emote into CES provided a name and a url.
    '''
    collection = ctx.bot.db.Emotes
    emote_channel = ctx.bot.emote_channels[ctx.guild_id]
    
    file_bytes = BytesIO()
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            file_bytes.write(await resp.read())
            file_bytes.seek(0)

    ext = what(None, h=file_bytes)
    # determine the file extension
    file_bytes.seek(0)
    if ext is None:
        raise ValueError(
            "Could not download emote. Check that you are actually linking to an image or GIF.")

    if emote_type == "auto":
        # Automatically make inline
        im = Image.open(file_bytes)
        file_bytes.seek(0)
        emote_type = "inline" if max(im.size) < 256 else "big"

    msg = await emote_channel.send(
        file=File(file_bytes, filename=f"{name}.{ext}"))

    collection.insert_one(
        {"name": name,
         "server": ctx.guild.id,
         "type": emote_type,
         "ext": ext,
         "URL": str(msg.attachments[0].url),
         "size": msg.attachments[0].size})

    return emote_type


async def inject(ctx: InteractionContext, name) -> CustomEmoji:
    '''
    Attempts to inject image into the server's list of emoji,
    returning it afterward
    '''
    collection = ctx.bot.db.Emotes
    
    if document := collection.find_one(
            {"name": name, "server": ctx.guild_id}):

        LIMIT = ctx.guild.emoji_limit
        all_custom_emojis: list[CustomEmoji] = \
            await ctx.guild.get_all_custom_emojis()

        # UNLOAD EMOJI
        if len(all_custom_emojis) >= LIMIT - 1:

            unload: CustomEmoji = all_custom_emojis[0]
            # emoji to be unloaded -- oldest one

            if not collection.find_one(
                    {"name": unload.name, "server": ctx.guild_id}):
                # If not loaded, we must first database it

                await upload(ctx, unload.name, str(unload.url), "inline")
                # upload the about-to-be-destroyed emoji

            await unload.delete()

        # LOAD NEW EMOJI
        file_bytes = BytesIO()
        async with aiohttp.ClientSession() as session:
            async with session.get(document["URL"]) as resp:
                file_bytes.write(await resp.read())
                file_bytes.seek(0)

        return await ctx.guild.create_custom_emoji(
            name=document["name"], imagefile=file_bytes)

    else:
        await ctx.send(f"Emote `{name}` was not found in the database.")
        return None
