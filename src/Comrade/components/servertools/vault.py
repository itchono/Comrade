import discord
from discord.ext import commands

import random
from async_lru import alru_cache

from db import collection
from utils.echo import echo
from utils.reactions import reactOK
from utils.checks import isOP
from config import cfg


# Janky workaround of cacheing stuff properly, but oh well
@alru_cache(maxsize=8)
async def vault_posts(guild_id: int):
    pass


class Vault(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.guild_only()
    async def randomvaultpost(self, ctx: commands.Context):
        '''
        Returns a random post from the vault.
        '''
        item = random.choice(self.vault_cache[ctx.guild.id])

        if item["type"] == "echo":
            targetmsg = await commands.MessageConverter().convert(ctx, item["data"])
            await echo(ctx, member=targetmsg.author, content=targetmsg.content, file=targetmsg.file, embed=targetmsg.embed)

        else:
            embed = discord.Embed()
            embed.set_image(url=item["data"])
            await ctx.send(embed=embed)

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
        elif u := await commands.MessageConverter().convert(ctx, tgt):
            IDmode = True
        else:
            u = tgt  # URL directly

        duration = collection("servers").find_one(ctx.guild.id)[
            "durations"]["vault"]

        m = await ctx.send(
            f"React to this message with 🍅 to vault the post {ctx.message.jump_url if not IDmode else u.jump_url}. You have **{duration} seconds** to vote.",
            delete_after=duration, embed=None)

        await m.add_reaction("🍅")

        def check(reaction, user):
            return reaction.emoji == "🍅" and not user.bot and (
                (reaction.message.id == m.id and user != ctx.author)
                or cfg["Settings"]["development-mode"] == "True"
                or isOP()(ctx))

        await self.bot.wait_for("reaction_add", check=check, timeout=duration)

        vault = ctx.guild.get_channel(
            collection("servers").find_one(ctx.guild.id)["channels"]["vault"])

        if IDmode:
            e = discord.Embed(
                title=":tomato: Echoed Vault Entry",
                description="See Echoed Message Below.")
            e.add_field(name='Original Post: ', value=ctx.message.jump_url)
            e.set_footer(text=f"Sent by {ctx.author.display_name}")
            m2 = await vault.send(embed=e)

            await echo(await self.bot.get_context(m2), member=u.author, content=u.content, file=await u.attachments[0].to_file() if u.attachments else None, embed=u.embeds[0] if u.embeds else None)
        else:
            e = discord.Embed(
                title=":tomato: Vault Entry")
            e.set_image(url=u)
            e.add_field(name='Original Post: ', value=ctx.message.jump_url)
            e.set_footer(text=f"Sent by {ctx.author.display_name}")
            await vault.send(embed=e)

        await reactOK(ctx)
        # rebuild vault cache
        await self.rebuildcache(ctx.guild)

        await m.edit(content="Vault operation successful.", embed=None)
