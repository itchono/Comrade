from utils.utilities import *
from utils.mongo_interface import *


class Vault(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activeposts = {}  # active for tomato stuff
        self._last_member = None

    @commands.command()
    @commands.check(isServer)
    async def randomvaultpost(self, ctx: commands.Context):
        '''
        Returns a random post from the vault. TODO
        '''
        await ctx.trigger_typing()
        vault = await getChannel(ctx.guild, "vault channel")
        msgs = await vault.history(limit=None).flatten()
        await ctx.send(random.choice(msgs).jump_url)

    @commands.command(name=u"\U0001F345", aliases = ["vault"])
    @commands.check(isServer)
    async def tomato(self, ctx: commands.Context, tgt=None):
        '''
        Vaults a post. Operates in 3 modes
        1. Vault a message sent by a user based on Message ID.
        ex. $c 🍅 711064013387071620
        2. Vault a message with an image attachment
        ex. $c 🍅    and then upload an image with this message
        3. Vault a message with an image url
        ex. $c 🍅 https://cdn.discordapp.com/attachments/419214713755402262/697604506975993896/2Q.png
        '''

        IDmode = False

        if len(ctx.message.attachments) > 0:
            u = ctx.message.attachments[0].url
        elif tgt and tgt.isnumeric():
            u = await ctx.fetch_message(int(tgt))
            IDmode = True
        else:
            u = tgt  # URL directly

        m = await ctx.send(
            "React to this message with 🍅 to vault the post {}".format(
                ctx.message.jump_url if not IDmode else u.jump_url))

        self.activeposts[m.id] = {
            "Message": ctx.message if not IDmode else u,
            "Attachment URL": u if not IDmode else None
        }

        await m.add_reaction("🍅")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction,
                              user: discord.User):
        if reaction.emoji == "🍅":
            if reaction.count > 1 and reaction.message.id in self.activeposts and \
                    (user != self.activeposts[reaction.message.id]["Message"].author or DEVELOPMENT_MODE):
                attachment_url = self.activeposts[
                    reaction.message.id]["Attachment URL"]

                msg = self.activeposts[reaction.message.id]["Message"]

                vault = await getChannel(reaction.message.guild,
                                         "vault channel")

                if not attachment_url:

                    m = await vault.send("Vault operation in progress...")

                    e = discord.Embed(title=":tomato: Echoed Vault Entry",
                                      description="See Echoed Message Below.",
                                      colour=discord.Colour.from_rgb(r=215,
                                                                     g=52,
                                                                     b=42))
                    e.add_field(name='Original Post: ', value=msg.jump_url)
                    e.set_footer(text="Sent by {}".format(msg.author))
                    c = await self.bot.get_context(m)
                    E = self.bot.get_cog("Echo")
                    await vault.send(embed=e)
                    await E.echo(c, msg.content, msg.author.display_name)

                else:
                    # made by Slyflare

                    e = discord.Embed(title=":tomato: Vault Entry",
                                      colour=discord.Colour.from_rgb(r=215,
                                                                     g=52,
                                                                     b=42))
                    e.set_image(url=str(attachment_url))
                    e.add_field(name='Original Post: ', value=msg.jump_url)
                    e.set_footer(text="Sent by {}".format(msg.author))

                    await vault.send(embed=e)

                del self.activeposts[reaction.message.id]
                await reactOK(await self.bot.get_context(reaction.message))
                await reaction.message.edit(content="Vault operation successful.", embed=None)
