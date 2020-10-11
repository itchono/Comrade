import discord
from discord.ext import commands
from utils import *

import random

class Vault(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vault_cache = {}
        

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

    @commands.command(name=u"\U0001F345", aliases = ["vault"])
    @commands.guild_only()
    async def tomato(self, ctx: commands.Context, tgt=None):
        '''
        Vaults a post. Operates in 3 modes
        1. Vault a message sent by a user based on Message URL.
        ex. $c 🍅 <link to message>
        2. Vault a message with an image attachment
        ex. $c 🍅 and then upload an image with this message
        3. Vault a message with an image url
        ex. $c 🍅 <link to image>
        '''
        IDmode = False

        if len(ctx.message.attachments) > 0:
            u = ctx.message.attachments[0].url
        elif tgt and tgt.isnumeric():
            u = await commands.MessageConverter().convert(ctx, tgt)
            IDmode = True
        elif u := await commands.MessageConverter().convert(ctx, tgt):
            IDmode = True
        else: u = tgt  # URL directly

        VAULT_VOTE_DURATION = DBcfgitem(ctx.guild.id,"vault-vote-duration")

        m = await ctx.send(
            "React to this message with 🍅 to vault the post {}. You have **{} seconds** to vote.".format(
                ctx.message.jump_url if not IDmode else u.jump_url, VAULT_VOTE_DURATION), delete_after=VAULT_VOTE_DURATION)

        await m.add_reaction("🍅")

        def check(reaction, user): return reaction.emoji == "🍅" and not user.bot and ((reaction.message.id == m.id and user != ctx.author) or DEVELOPMENT_MODE)

        await self.bot.wait_for("reaction_add", check=check)

        vault = await getChannel(ctx.guild,"vault-channel")

        if IDmode: 
            e = discord.Embed(title=":tomato: Echoed Vault Entry", description="See Echoed Message Below.", colour=discord.Colour.from_rgb(*DBcfgitem(ctx.guild.id,"theme-colour")))
            e.add_field(name='Original Post: ', value=ctx.message.jump_url)
            e.set_footer(text=f"Sent by {ctx.author.display_name}")
            m2 = await vault.send(embed=e)

            await echo(await self.bot.get_context(m2), member=u.author, content=u.content, file=u.attachments[0] if u.attachments else None, embed=u.embeds[0] if u.embeds else None)
        else:
            e = discord.Embed(title=":tomato: Vault Entry", colour=discord.Colour.from_rgb(*DBcfgitem(ctx.guild.id,"theme-colour")))
            e.set_image(url=u)
            e.add_field(name='Original Post: ', value=ctx.message.jump_url)
            e.set_footer(text=f"Sent by {ctx.author.display_name}")
            await vault.send(embed=e)

        await reactOK(ctx)
        # rebuild vault cache
        await self.rebuildcache(ctx.guild)

        await m.edit(content="Vault operation successful.", embed=None)

    async def rebuildcache(self, g:discord.Guild):
        '''
        Rebuilds vault cache
        '''
        if vault := await getChannel(g, "vault-channel"):
            msgs = await vault.history(limit=None).flatten()

            posts = []

            for m in msgs:
                if len(m.embeds):
                    if m.embeds[0].image:
                        # vaulted embedded image
                        posts.append({"type":"img", "data":m.embeds[0].image.url})
                    elif m.embeds[0].url:
                        posts.append({"type":"img", "data":m.embeds[0].url})
                    else:
                        posts.append({"type":"echo", "data":m.id})

            self.vault_cache[g.id] = posts
            await log(g, f"Vault Cache built with {len(posts)} entries.")

    async def on_load(self):
        '''
        When bot is loaded
        '''
        for g in self.bot.guilds: await self.rebuildcache(g)
        print('Vault Cache Ready')