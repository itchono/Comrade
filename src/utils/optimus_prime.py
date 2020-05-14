from utils.utilities import *
from utils.mongo_interface import *

class Prime(commands.Cog):
    '''
    Comrade moderation module
    '''
    def __init__(self, bot):
        self.bot = bot
        self.activemsgids = [] # active for ZAHANDO
        self._last_member = None

    async def zahando(self, ctx:commands.Context, num:int=20, user:discord.User=None):
        '''
        erases a set number of messages in a context (Default 20)
        '''
        setTGT(user)
        await ctx.channel.purge(limit=num, check=purgeCheck if user else None)

        with open("vid/Za_Hando_erase_that.mp4", "rb") as f:
            m = await ctx.send(content="ZA HANDO Successful.", file=discord.File(f, "ZA HANDO.mp4"))
            await log(ctx.guild, "ZA HANDO in {}".format(ctx.channel.name))
            await asyncio.sleep(10)
            await m.delete()

    @commands.Cog.listener()
    async def on_message(self, message:discord.message):
        if not message.author.bot:
            if "za hando" in message.content.lower():
                m = await message.channel.send("React with '✋' to purge the channel.")
                self.activemsgids.append(m.id)
                await m.add_reaction("✋")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:discord.Reaction, user:discord.User):
        if reaction.emoji == "✋":
            if (reaction.count > getCFG(reaction.message.guild.id)["zahando threshold"] or isUserOP(user)) and reaction.message.id in self.activemsgids:
                await self.zahando(await self.bot.get_context(reaction.message))
                self.activemsgids.remove(reaction.message.id)