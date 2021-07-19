import discord
from discord.ext import commands

import random
import asyncio
from async_lru import alru_cache

from db import collection
from utils.echo import echo, mimic
from utils.reactions import reactOK
from utils.checks import isOP
from utils.utilities import utc_to_local_time
from config import cfg

from client import discord_client as bot


# Janky workaround of cacheing stuff properly, but oh well
@alru_cache(maxsize=8)
async def vault_posts(guild_id: int):
    vault: discord.TextChannel = bot.get_channel(
            collection("servers").find_one(guild_id)["channels"]["vault"])
    return (await vault.history(limit=None).flatten())


class Vault(commands.Cog):
    '''
    User-curated archive of good posts
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.guild_only()
    async def randomvaultpost(self, ctx: commands.Context):
        '''
        Returns a random post from the vault.
        '''
        message = random.choice(vault_posts(ctx.guild.id))

        await echo(ctx, member=message.author, content=message.content,
                        file=await message.attachments[0].to_file() if message.attachments else None,
                        embed=message.embeds[0] if message.embeds else None)

    @commands.command(aliases=[u"\U0001F345"])
    @commands.guild_only()
    async def vault(self, ctx: commands.Context, tgt=None):
        '''
        Vaults a post. Operates in 3 modes
        1. Vault a message sent by a user based on Message URL.
        ex. $c vault <link to message>
        2. Vault a message with an image attachment
        ex. $c vault and then upload an image with this message
        3. Vault a message with an image url
        ex. $c vault <link to image>
        '''
        IDmode = False

        if ctx.message.attachments:
            u = ctx.message.attachments[0].url
        elif tgt and tgt.isnumeric():
            u = await commands.MessageConverter().convert(ctx, tgt)
            IDmode = True
        else:
            try:
                u = await commands.MessageConverter().convert(ctx, tgt)
                IDmode = True
            except Exception:
                u = tgt  # URL directly

        duration = collection("servers").find_one(ctx.guild.id)[
            "durations"]["vault"]


        ee = discord.Embed(color=0xd7342a,
                        description= f"React to this message with 🍅 to vault [this post]({ctx.message.jump_url if not IDmode else u.jump_url})"
                        f"\nYou have **{duration} seconds** to vote.")

        m = await ctx.send(embed=ee, delete_after=duration)

        await m.add_reaction("🍅")

        def check(reaction, user):
            return reaction.emoji == "🍅" and not user.bot and (
                (reaction.message.id == m.id and user != ctx.author)
                or cfg["Settings"]["development-mode"] == "True"
                or isOP()(ctx))
        try:
            await self.bot.wait_for("reaction_add", check=check, timeout=duration)

            vault = ctx.guild.get_channel(
                collection("servers").find_one(ctx.guild.id)["channels"]["vault"])

            if IDmode:
                e = discord.Embed(color=0xd7342a,
                    description=f"[Source Message]({u.jump_url})")
                e.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                e.set_footer(
                    text=f"Originally sent in #{ctx.channel.name}, at {utc_to_local_time(u.created_at).strftime('%B %d %Y at %I:%M:%S %p %Z')}")
                await mimic(vault, content=u.content,
                username=u.author.display_name, avatar_url=u.author.avatar_url,
                file=await u.attachments[0].to_file() if u.attachments else None,
                embeds=u.embeds + [e] if u.embeds else [e])

            else:
                e = discord.Embed(color=0xd7342a,
                    description=f"[Source Message]({ctx.message.jump_url})")
                e.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                e.set_image(url=u)
                e.set_footer(
                    text=f"Originally sent in #{ctx.channel.name}, at {utc_to_local_time(ctx.message.created_at).strftime('%B %d %Y at %I:%M:%S %p %Z')}")
                await vault.send(embed=e)

            await reactOK(ctx)
            # rebuild vault cache
            vault_posts.cache_clear()

            await m.edit(content="Vault operation successful.", embed=None)
        except asyncio.TimeoutError:
            await m.edit(content="Vault aborted (180s timeout).", embed=None)
