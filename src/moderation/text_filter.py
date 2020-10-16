import discord
from discord.ext import commands
from utils import *
from utils.additional import *

# Text Filtering
import re
import unidecode
# ALSO: need python-levenshtein ==> needs C++ build tools installed
from fuzzywuzzy import fuzz # NOTE: install python-Levenshtein for faster results.
from utils.checks.other_checks import *

class TextFilter(commands.Cog):
    '''
    Comrade moderation module
    '''
    def __init__(self, bot):
        self.bot = bot
        self.activepurge = {}  # active for ZAHANDO
        '''
        Stores stuff like
        {1231240914120412:{"User":@Some user, "Amount":20, "Perpetrator":<some user object>}, ....}
        '''

        self.bucket = {} # stores a bunch of messages
        

    async def zahando(self,
                      ctx: commands.Context,
                      num: int = 20,
                      user: discord.User = None, perpetrator = None):
        '''
        erases a set number of messages in a context (Default 20)
        '''
        if user: await ctx.channel.purge(limit=num, check=purgeCheck(user))
        else: await ctx.channel.purge(limit=num)

        with open("vid/Za_Hando_erase_that.mp4", "rb") as f:
            await ctx.send(content="ZA HANDO Successful.", file=discord.File(f, "ZA HANDO.mp4"), delete_after=10)
            await log(ctx.guild, f"ZA HANDO in {ctx.channel.mention}, performed by {perpetrator.mention})")

    async def additionalChecks(self, message: discord.Message):
        '''
        Checks a message for additional offending characteristics based on user
        '''
        try:
            u = DBuser(message.author.id, message.guild.id)
            if (u["stop-pings"] and message.mentions) or (u["stop-images"] and (message.attachments or message.embeds)):
                await echo(await self.bot.get_context(message), member=message.author, content="```I sent a bad message: " + message.content + "```")
                return True
        except:
            # if it's not in a server
            return False
            
    def filter(self, ctx: commands.Context, content: str):
        '''
        Detects if the string violates the moderation guidelines for a given context.
        '''
        spaced_query = unidecode.unidecode(emojiToText(content.lower()))
        # remove non-ascii, attempt to decode unicode, get into formattable form
        query = re.sub("\W+", '', spaced_query) # spaces

        words = DBcfgitem(ctx.guild.id, "banned-words")
        words.update(DBuser(ctx.author.id, ctx.guild.id)["banned-words"])

        # TODO with python 3.9 -- dictionary union
        for w in words:

            if words[w] < 100 and (len(query) > 2 and fuzz.partial_ratio(query, w) >= words[w]) or query == w: return True

            for word in spaced_query.split(" "):
                if word[0] == w[0] and word[-1] == w[-1] and fuzz.partial_ratio(word, w) >= words[w]: return True
                # checking endcap letters

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
                    ZA_HANDO_VOTE_DURATION = DBcfgitem(message.guild.id,"za-hando-vote-duration")

                    m = await message.channel.send(
                        "React with '✋' to purge the channel of {} messages {}. You have **{} seconds** to vote.".
                        format(
                            amount,
                            ("from " +
                            str(message.mentions[0])) if message.mentions else "", ZA_HANDO_VOTE_DURATION), delete_after=ZA_HANDO_VOTE_DURATION
                    )
                    self.activepurge[m.id] = {
                        "amount": amount,
                        "user": message.mentions[0] if message.mentions else None,
                        "perpetrator": message.author
                    }

                    await m.add_reaction("✋")

            # moderation system
            ctx = await self.bot.get_context(message)

            if self.filter(ctx, message.content) or await self.additionalChecks(message):
                await message.delete()
            else:
                try: 
                    self.bucket[message.guild.id][message.author.id] += [message]

                    joined = " ".join([m.content for m in self.bucket[message.guild.id][message.author.id]])
                    if self.filter(ctx, joined):
                        for m in self.bucket[message.guild.id][message.author.id]:
                            try:  await m.delete()
                            except: print("Cannot delete message {}".format(m.content))
                        self.bucket[message.guild.id][message.author.id] = []
                    
                    elif len(self.bucket[message.guild.id][message.author.id]) > MSG_BUFFER_LIMIT:
                        self.bucket[message.guild.id][message.author.id].pop(0)
                except:
                    try:
                        self.bucket[message.guild.id] = {}
                        self.bucket[message.guild.id][message.author.id] = [message]
                    except: pass


    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        '''
        Catch people trying to edit messages
        '''
        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id) if not payload.cached_message else payload.cached_message

        if not message.author.bot and message.guild:
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
            if (reaction.count > DBcfgitem(
                    reaction.message.guild.id, "zahando-threshold")
                    or user.id in [i["user"] for i in getOPS(reaction.message.guild.id)]
                ) and reaction.message.id in self.activepurge:
                await self.zahando(
                    await self.bot.get_context(reaction.message),
                    self.activepurge[reaction.message.id]["amount"],
                    self.activepurge[reaction.message.id]["user"], self.activepurge[reaction.message.id]["perpetrator"])
                del self.activepurge[reaction.message.id]
