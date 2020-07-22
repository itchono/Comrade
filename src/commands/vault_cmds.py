from utils.utilities import *
from utils.mongo_interface import *
from utils.database_utils import *


class Vault(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activeposts = {}  # active for tomato stuff
        self.vault_cache = {}
        self._last_member = None

    @commands.command()
    @commands.guild_only()
    async def randomvaultpost(self, ctx: commands.Context):
        '''
        Returns a random post from the vault.
        '''
        item = random.choice(self.vault_cache[ctx.guild.id])

        if item["type"] == "echo":
            targetmsg = await commands.MessageConverter().convert(ctx, item["data"])
            c = self.bot.get_cog("Echo")
            await c.echo(ctx, targetmsg.content, str(targetmsg.author.name), deleteMsg=False)
        else:
            embed = discord.Embed()
            embed.set_image(url=item["data"])
            await ctx.send(embed=embed)

    @commands.command(name=u"\U0001F345", aliases = ["vault"])
    @commands.guild_only()
    async def tomato(self, ctx: commands.Context, tgt=None):
        '''
        Vaults a post. Operates in 3 modes
        1. Vault a message sent by a user based on Message ID.
        ex. $c 🍅 711064013387071620
        2. Vault a message with an image attachment
        ex. $c 🍅 and then upload an image with this message
        3. Vault a message with an image url
        ex. $c 🍅 https://cdn.discordapp.com/attachments/419214713755402262/697604506975993896/2Q.png
        '''
        IDmode = False

        if len(ctx.message.attachments) > 0:
            u = ctx.message.attachments[0].url
        elif tgt and tgt.isnumeric():
            u = await commands.MessageConverter().convert(tgt)
            IDmode = True
        else: u = tgt  # URL directly

        VAULT_VOTE_DURATION = DBcfgitem(ctx.guild.id,"vault-vote-duration")

        m = await ctx.send(
            "React to this message with 🍅 to vault the post {}. You have **{} seconds** to vote.".format(
                ctx.message.jump_url if not IDmode else u.jump_url, VAULT_VOTE_DURATION), delete_after=VAULT_VOTE_DURATION)

        self.activeposts[m.id] = {
            "Message": ctx.message if not IDmode else u,
            "Attachment URL": u if not IDmode else None
        }

        await m.add_reaction("🍅")

    async def rebuildcache(self, g:discord.Guild):
        '''
        Rebuilds vault cache
        '''
        if vault := await getChannel(g, "vault channel"):
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
                        posts.append({"type":"echo", "data":m.embeds[0].fields[0].value})

            self.vault_cache[g.id] = posts
            await log(g, f"Vault Cache built with {len(posts)} entries.")

    async def on_load(self):
        '''
        When bot is loaded
        '''
        for g in self.bot.guilds: await self.rebuildcache(g)
        print('Vault Cache Ready')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction,
                              user: discord.Member):
        if reaction.emoji == "🍅":
            if reaction.count > 1 and reaction.message.id in self.activeposts and (user != self.activeposts[reaction.message.id]["Message"].author or DEVELOPMENT_MODE):
                attachment_url = self.activeposts[reaction.message.id]["Attachment URL"]

                msg = self.activeposts[reaction.message.id]["Message"]

                vault = await getChannel(reaction.message.guild,"vault channel")

                if not attachment_url:
                    m = await vault.send("Vault operation in progress...")
                    e = discord.Embed(title=":tomato: Echoed Vault Entry",
                                      description="See Echoed Message Below.",
                                      colour=discord.Colour.from_rgb(*DBcfgitem(ctx.guild.id,"theme-colour")))
                    e.add_field(name='Original Post: ', value=msg.jump_url)
                    e.set_footer(text="Sent by {}".format(msg.author))
                    c = await self.bot.get_context(m)
                    E = self.bot.get_cog("Echo")
                    await vault.send(embed=e)
                    await E.echo(c, msg.content, msg.author.display_name)

                else:
                    # made by Slyflare
                    e = discord.Embed(title=":tomato: Vault Entry",
                                      colour=discord.Colour.from_rgb(*DBcfgitem(ctx.guild.id,"theme-colour")))
                    e.set_image(url=str(attachment_url))
                    e.add_field(name='Original Post: ', value=msg.jump_url)
                    e.set_footer(text="Sent by {}".format(msg.author))

                    await vault.send(embed=e)

                del self.activeposts[reaction.message.id]
                await reactOK(await self.bot.get_context(reaction.message))
                await reaction.message.edit(content="Vault operation successful.", embed=None)

                # rebuild vault cache
                await self.rebuildcache(reaction.message.guild)