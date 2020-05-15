from utils.utilities import *
from utils.mongo_interface import *

class Vault(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.activeposts = {} # active for tomato stuff
        self._last_member = None

    @commands.command()
    async def randomvaultpost(self, ctx:commands.Context):
        '''
        Returns a random post from the vault.
        '''
        vault = getChannel(ctx.guild, "vault channel")

        msgs = vault.messages

    @commands.command(name=u"\U0001F345")
    async def tomato(self, ctx:commands.Context, url:str=None):
        '''
        Vaults a post.
        '''
        
        if len(ctx.message.attachments) > 0:
            u = ctx.message.attachments[0].url
        else:
            u = url
        
        m = await ctx.send("React to this message with 🍅 to vault the post {}".format(ctx.message.jump_url))

        self.activeposts[m.id] = {"Message":ctx.message, "Attachment URL":u}

        await m.add_reaction("🍅")

    @commands.command()
    async def vault(self, ctx:commands.Context, url:str=None):
        '''
        Alias for vault
        '''
        await self.tomato(ctx, url)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:discord.Reaction, user:discord.User):
        if reaction.emoji == "🍅":
            if reaction.count > 1 and reaction.message.id in self.activeposts and user != self.activeposts[reaction.message.id]["Message"].author:
                
                attachment_url = self.activeposts[reaction.message.id]["Attachment URL"]
                msg = self.activeposts[reaction.message.id]["Message"]

                vault = await getChannel(reaction.message.guild, "vault channel")

                #VIMAL DO STUFF HERE
                '''
                Maybe:
                author = msg.author
                channel = msg.channel
                '''

                await vault.send("Vimal Code this")


                del self.activeposts[reaction.message.id]
