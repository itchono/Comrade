from utils.utilities import *
from utils.mongo_interface import *

class Prime(commands.Cog):
    '''
    Comrade moderation module
    '''
    def __init__(self, bot):
        self.bot = bot
        self.activepurge = {} # active for ZAHANDO
        '''
        Stores stuff like
        {1231240914120412:{"User":@Some user, "Amount":20}, ....}
        '''
        self._last_member = None

    async def zahando(self, ctx:commands.Context, num:int=20, user:discord.User=None):
        '''
        erases a set number of messages in a context (Default 20)
        '''
        setTGT(user)
        if user:
            await ctx.channel.purge(limit=num, check=purgeCheck)
        else:
            await ctx.channel.purge(limit=num)

        with open("vid/Za_Hando_erase_that.mp4", "rb") as f:
            m = await ctx.send(content="ZA HANDO Successful.", file=discord.File(f, "ZA HANDO.mp4"))
            await log(ctx.guild, "ZA HANDO in {}".format(ctx.channel.name))
            await asyncio.sleep(10)
            await m.delete()

    @commands.Cog.listener()
    async def on_message(self, message:discord.message):
        if not message.author.bot:
            if "za hando" in message.content.lower():

                args = (message.content.lower()).split()
                amount = 20

                if len(args) > 2 and args[2].isnumeric():
                    amount = eval(args[2])

                m = await message.channel.send("React with '✋' to purge the channel of {} messages {}".format(amount,"from " + str(message.mentions[0] if message.mentions else None)))
                self.activepurge[m.id] = {}
                self.activepurge[m.id]["amount"] = amount
                self.activepurge[m.id]["user"] = message.mentions[0] if message.mentions else None
                
                await m.add_reaction("✋")

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:discord.Reaction, user:discord.User):
        if reaction.emoji == "✋":
            if (reaction.count > getCFG(reaction.message.guild.id)["zahando threshold"] or isUserOP(user)) and reaction.message.id in self.activepurge:
                await self.zahando(await self.bot.get_context(reaction.message), self.activepurge[reaction.message.id]["amount"], self.activepurge[reaction.message.id]["user"])
                del self.activepurge[reaction.message.id]