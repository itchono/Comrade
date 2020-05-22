from utils.utilities import *
from utils.mongo_interface import *
from utils.emoji_converter import *
import urllib.request
from bs4 import BeautifulSoup

class Fun(commands.Cog):
    '''
    Extensive work by Kevinozoid
    '''
    def __init__(self, bot):
        self.bot = bot
        self.activetrivia = {}
        self._last_member = None

    # TODO: add moderation checks
    @commands.command()
    async def textToEmoji(self, ctx, *, text):
        await ctx.send(textToEmoji(text))

    @commands.command()
    async def emojiToText(self, ctx, *, text):
        await ctx.send(emojiToText(text))

    @commands.command()
    @commands.check(isnotThreat)
    async def surprise(self, ctx: commands.Context):
        '''
        nuke
        '''
        await ctx.send("nuke deploying in")
        await ctx.send("5")
        await ctx.send("4")
        await ctx.send("3")
        await ctx.send("2")
        await ctx.send("no")
           
    @commands.command()
    @commands.check(isnotThreat)
    async def fanfic(self,ctx: commands.Context, site):
        '''
        initiate fanfiction
        '''
        req = urllib.request.urlopen(site, timeout=10)
        html = req.read()
        soup = BeautifulSoup(html)

        for script in soup(["script", "style"]):
            script.extract() 

        holyText = soup.get_text()

        lines = (line.strip() for line in holyText.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        string = []

        for s in chunks:
            if len(s)>2000:
                while len(s)>2000:
                    string.append(s[0:2000])
                    s = s[2000:len(s)]
            string.append(s)

        for s in string:
            if not s=='' and not s==' ' and not s== '  ' and len(s)>20:
                await ctx.send(s)

    @commands.command()
    @commands.check(isnotThreat)
    async def detectBad(self, ctx: commands.Context):
        '''
        nuke
        '''
        if (ctx.author== await (extractUser(self.bot,ctx,"itchono"))):
            await ctx.send("you are in fact bad")
        else:
            await ctx.send("you are in fact non-bad")

    @commands.command()
    @commands.check(isnotThreat)
    async def quiz(self, ctx: commands.Context):
        '''
        quiz
        '''
        check = True
        req = urllib.request.urlopen("https://pastebin.com/raw/2PjhRjtn", timeout = 10)
        questions = req.read().decode().splitlines()
        questions.remove("")
        while check:
            count = 0
            random.seed()
            check = False
            element = round(random.random() * (len(questions)-1))
            while not any(char.isdigit() for char in questions[element][0:2]) or not "." in questions[element][0:5]:
                element = round(random.random() * (len(questions)-1))

            m = await ctx.send(questions[element])
            counter = 1
            while not questions[element+counter].find('D)')==0:
                if not questions[element+counter]=="" and not questions[element+counter]==" ":
                    await ctx.send(questions[element+counter])
                counter+=1
                count+=1
            await ctx.send(questions[element+counter])

            if " A" in questions[element+counter+1] or " A" in questions[element+counter+2]:
                self.activetrivia[m.id] = 1
            elif " B" in questions[element+counter+1] or " B" in questions[element+counter+2]:
                self.activetrivia[m.id] = 2
            elif " C" in questions[element+counter+1] or " C" in questions[element+counter+2]:
                self.activetrivia[m.id] = 3
            elif " D" in questions[element+counter+1] or " D" in questions[element+counter+2]:
               self.activetrivia[m.id] = 4
            else:
                await(ctx.send("SOMETHING BROKE"))

            await m.add_reaction("1️⃣")
            await m.add_reaction("2️⃣")
            await m.add_reaction("3️⃣")
            await m.add_reaction("4️⃣")
            await asyncio.sleep(count*5)
            await m.remove_reaction("1️⃣", self.bot.user)
            await m.remove_reaction("2️⃣", self.bot.user)
            await m.remove_reaction("3️⃣", self.bot.user)
            await m.remove_reaction("4️⃣", self.bot.user)
            
            m2 = await ctx.channel.fetch_message(m.id)

            for u in m2.reactions:
                async for u2 in u.users():
                    if (u2==self.bot.user):
                        check = True

            if not check:
                await ctx.send("Nobody said anything so you all get chlamydia!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        '''
        Emoji call listener
        '''
        if message.content.lower()[0:3] == "tte":
            await self.textToEmoji(await self.bot.get_context(message), text=message.content.lower().strip("tte "))
        elif message.content.lower()[0:3] == "ett":
            await self.emojiToText(await self.bot.get_context(message), text=message.content.lower().strip("ett "))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:discord.Reaction, user:discord.User):
        '''
        When a user adds a reaction to a message.
        '''
        m=reaction.message
        checker = False
        async for u in reaction.users():
            if(u==self.bot.user): 
                checker = True

        if reaction.message.author == self.bot.user and ((reaction.emoji == "4️⃣" and self.activetrivia[m.id] == 4) or (reaction.emoji == "3️⃣" and self.activetrivia[m.id] == 3) or (reaction.emoji == "2️⃣" and self.activetrivia[m.id] == 2) or (reaction.emoji == "1️⃣" and self.activetrivia[m.id] == 1)) and checker and user != self.bot.user:
            await reaction.message.add_reaction("☑")
            await reaction.message.channel.send(user.mention + " you have some brain")
        elif reaction.message.author == self.bot.user and reaction.emoji == "1️⃣" and checker and user != self.bot.user:
            await reaction.message.add_reaction("🅱")
            await reaction.message.channel.send(user.mention + " you're a twat.")
        elif reaction.message.author == self.bot.user and reaction.emoji == "2️⃣" and checker and user != self.bot.user:
            await reaction.message.add_reaction("🅱")
            await reaction.message.channel.send(user.mention + " you're a twoat.")
        elif reaction.message.author == self.bot.user and reaction.emoji == "3️⃣" and checker and user != self.bot.user:
            await reaction.message.add_reaction("🅱")
            await reaction.message.channel.send(user.mention + " you're a twat.")
        elif reaction.message.author == self.bot.user and reaction.emoji == "4️⃣" and checker and user != self.bot.user:
            await reaction.message.add_reaction("🅱")
            await reaction.message.channel.send(user.mention + " you're a twat.")


