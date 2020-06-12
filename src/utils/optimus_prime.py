from utils.utilities import *
from utils.mongo_interface import *

# Text Filtering
import re
import unidecode
# ALSO: need python-levenshtein ==> needs C++ build tools installed
from fuzzywuzzy import fuzz

class Prime(commands.Cog):
    '''
    Comrade moderation module
    '''
    def __init__(self, bot):
        self.bot = bot
        self.activepurge = {}  # active for ZAHANDO
        '''
        Stores stuff like
        {1231240914120412:{"User":@Some user, "Amount":20}, ....}
        '''

        self.bucket = {} # stores a bunch of messages
        self._last_member = None

    async def zahando(self,
                      ctx: commands.Context,
                      num: int = 20,
                      user: discord.User = None):
        '''
        erases a set number of messages in a context (Default 20)
        '''
        setTGT(user)
        if user:
            await ctx.channel.purge(limit=num, check=purgeCheck)
        else:
            await ctx.channel.purge(limit=num)

        with open("vid/Za_Hando_erase_that.mp4", "rb") as f:
            m = await ctx.send(content="ZA HANDO Successful.",
                               file=discord.File(f, "ZA HANDO.mp4"))
            await log(ctx.guild, "ZA HANDO in {}".format(ctx.channel.name))
            await asyncio.sleep(10)
            await m.delete()

    async def additionalChecks(self, message: discord.Message):
        '''
        Checks a message for additional offending characteristics based on user
        '''
        try:
            u = getUser(message.author.id, message.guild.id)
            if (u["stop pings"] and len(message.mentions) > 0) or (u["stop images"] and (len(message.attachments) > 0 or len(message.embeds) > 0)):
                c = self.bot.get_cog("Echo")
                await c.echo(await self.bot.get_context(message), "```I sent a bad message: " + message.content + "```", str(message.author.id), deleteMsg=False)
                return True
            return u["muted"]
        
        except:
            # if it's not in a server
            return False
            
    def filter(self, ctx: commands.Context, content: str):
        '''
        Detects if the string violates the moderation guidelines for a given context.
        Optionally takes in message as filter parameter to stop images and pings
        '''
        query = re.sub("\W+", '', unidecode.unidecode(content.lower()))
        # remove spaces, remove non-ascii, get into formattable form

        u = getUser(ctx.author.id, ctx.guild.id)
        c = getCFG(ctx.guild.id)

        words = u["banned words"] + c["banned words"]

        for w in words:
            if (len(query) > 3 and fuzz.partial_ratio(query, w) >= 80) or fuzz.ratio(query, w) >= 70:
                return True

        return False
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if not message.author.bot and message.guild:
            if "ZA HANDO" in message.content:
                args = (message.content.lower()).split()
                amount = 20

                if len(args) > 2 and args[2].isnumeric():
                    amount = int(args[2])

                if amount > 200 and not isOP(await self.bot.get_context(message)):
                    await message.channel.send("No")
                else:
                    m = await message.channel.send(
                        "React with '✋' to purge the channel of {} messages {}. You have **{} seconds** to vote.".
                        format(
                            amount,
                            ("from " +
                            str(message.mentions[0])) if message.mentions else "", ZA_HANDO_VOTE_DURATION), delete_after=ZA_HANDO_VOTE_DURATION
                    )
                    self.activepurge[m.id] = {
                        "amount": amount,
                        "user": message.mentions[0] if message.mentions else None
                    }

                    await m.add_reaction("✋")

            # moderation system
            ctx = await self.bot.get_context(message)

            if self.filter(ctx, message.content) or await self.additionalChecks(message):
                await message.delete()
            else:
                try: self.bucket[message.guild.id][message.author.id] += [message]
                except:
                    try:
                        self.bucket[message.guild.id] = {}
                        self.bucket[message.guild.id][message.author.id] = [message]
                    except:
                        pass
                
                joined = "".join([m.content for m in self.bucket[message.guild.id][message.author.id]])

                if self.filter(ctx, joined):
                    for m in self.bucket[message.guild.id][message.author.id]:
                        try:
                            await m.delete()
                        except:
                            print("Cannot delete message {}".format(m.content))
                    self.bucket[message.guild.id][message.author.id] = []
                
                elif len(self.bucket[message.guild.id][message.author.id]) > MSG_BUFFER_LIMIT:
                    self.bucket[message.guild.id][message.author.id].pop(0)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.message, message: discord.message):
        '''
        Catch people trying to edit messages
        '''
        # moderation system
        ctx = await self.bot.get_context(message)

        if self.filter(ctx, message.content) or await self.additionalChecks(message):
            await message.delete()
        else:
            try: self.bucket[message.guild.id][message.author.id] += [message]
            except:
                try:
                    self.bucket[message.guild.id] = {}
                    self.bucket[message.guild.id][message.author.id] = [message]
                except:
                    pass
            
            joined = "".join([m.content for m in self.bucket[message.guild.id][message.author.id]])

            if self.filter(ctx, joined):
                for m in self.bucket[message.guild.id][message.author.id]:
                    try:
                        await m.delete()
                    except:
                        print("Cannot delete message {}".format(m.content))
                self.bucket[message.guild.id][message.author.id] = []
            
            elif len(self.bucket[message.guild.id][message.author.id]) > MSG_BUFFER_LIMIT:
                self.bucket[message.guild.id][message.author.id].pop(0)


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction,
                              user: discord.User):
        if reaction.emoji == "✋":
            if (reaction.count > getCFG(
                    reaction.message.guild.id)["zahando threshold"]
                    or user.id in [i["user"] for i in getOPS(reaction.message.guild.id)]
                ) and reaction.message.id in self.activepurge:
                await self.zahando(
                    await self.bot.get_context(reaction.message),
                    self.activepurge[reaction.message.id]["amount"],
                    self.activepurge[reaction.message.id]["user"])
                del self.activepurge[reaction.message.id]
