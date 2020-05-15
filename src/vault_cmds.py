from utils.utilities import *
from utils.mongo_interface import *


class Vault(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activeposts = {}  # active for tomato stuff
        self._last_member = None

    @commands.command()
    async def randomvaultpost(self, ctx: commands.Context):
        '''
        Returns a random post from the vault.
        '''
        vault = getChannel(ctx.guild, "vault channel")

        msgs = vault.messages

    @commands.command(name=u"\U0001F345")
    async def tomato(self, ctx: commands.Context, url: str = None):
        '''
        Vaults a post.
        '''

        if len(ctx.message.attachments) > 0:
            u = ctx.message.attachments[0].url
        elif tgt.isnumeric():
            u = ctx.fetch_message(eval(tgt))
        else:
            u = tgt
        
        m = await ctx.send("React to this message with 🍅 to vault the post {}".format(ctx.message.jump_url if not tgt.isnumeric() else u.jump_url))

        self.activeposts[m.id] = {"Message": ctx.message, "Attachment URL": u}

        await m.add_reaction("🍅")

    @commands.command()
    async def vault(self, ctx: commands.Context, url: str = None):
        '''
        Alias for vault
        '''
        await self.tomato(ctx, url)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        if reaction.emoji == "🍅":
            if reaction.count > 1 and reaction.message.id in self.activeposts and \
                    (user != self.activeposts[reaction.message.id]["Message"].author or DEVELOPMENT_MODE):
                attachment_url = self.activeposts[reaction.message.id]["Attachment URL"]
                msg = self.activeposts[reaction.message.id]["Message"]

                vault = await getChannel(reaction.message.guild, "vault channel")

                e = discord.Embed(title=":tomato: Vault Entry", colour=discord.Colour.from_rgb(r=215, g=52, b=42))
                e.set_image(url=str(attachment_url))
                e.add_field(name='Original Post: ',value=msg.jump_url)
                e.set_footer(text="Sent by {}".format(user))

                await vault.send(embed=e)

                del self.activeposts[reaction.message.id]
