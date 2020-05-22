from utils.utilities import *
from utils.mongo_interface import *
from utils.emoji_converter import *

import urllib.request
from bs4 import BeautifulSoup

import numpy as np
from numpy import *
import matplotlib.pyplot as plt
import parser
import io

class Fun(commands.Cog):
    '''
    Fun stuff.
    '''
    def __init__(self, bot):
        self.bot = bot
        self.activetrivia = {}
        self._last_member = None

    @commands.command()
    async def graph(self, ctx: commands.Context, function: str, xstart: int = -10, xend: int = 10):
        '''
        Graphs a single variable algebraic function in some domain.
        '''

        # TODO filter the function input
        function = function.replace("^", "**") # exponentiation

        stepsize = 500
        '''try:'''
        D = xend-xstart
        x = np.arange(xstart, xend, D/stepsize)

        fnc = parser.expr(function).compile()
        
        arr = eval(fnc)

        plt.plot(x, arr, label=function)

        plt.title("Plot Requested by {}".format(ctx.author.name))
        plt.ylabel("y")
        plt.xlabel("x")
        plt.legend()
        plt.axhline(y=0, color='k')
        plt.axvline(x=0, color='k')
        plt.grid()
        f = io.BytesIO()
        plt.savefig(f, format="png")
        f.seek(0)
        plt.clf()

        await ctx.send(file=discord.File(f, "graph.png"))

        '''except:
            await ctx.send("Something went wrong with parsing. Try again.")'''


    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def space(self, ctx):
        '''
        Posts text with stars and space. Best used on dark theme.
        '''

        await ctx.send(".　　　　　　　　　　 ✦ 　　　　   　 　　　˚　　　　　　　　　　　　　　*　　　　　　   　　　　　　　　　　　　　　　.　　　　　　　　　　　　　　. 　　 　　　　　　　 ✦ 　　　　　　　　　　 　 ‍ ‍ ‍ ‍ 　　　　 　　　　　　　　　　　　,　　   　\n\n.　　　　　　　　　　　　　.　　　ﾟ　  　　　.　　　　　　　　　　　　　.\n\n　　　　　　,　　　　　　　.　　　　　　    　　　　 　　　　　　　　　　　　　　　　　　 ☀️ 　　　　　　　　　　　　　　　　　　    　      　　　　　        　　　　　　　　　　　　　. 　　　　　　　　　　.　　　　　　　　　　　　　. 　　　　　　　　　　　　　　　　       　   　　　　 　　　　　　　　　　　　　　　　       　   　　　　　　　　　　　　　　　　       　    ✦ 　   　　　,　　　　　　　　　　　    🚀 　　　　 　　,　　　 ‍ ‍ ‍ ‍ 　 　　　　　　　　　　　　.　　　　　 　　 　　　.　　　　　　　　　　　　　 　           　　　　　　　　　　　　　　　　　　　˚　　　 　   　　　　,　　　　　　　　　　　       　    　　　　　　　　　　　　　　　　.　　　  　　    　　　　　 　　　　　.　　　　　　　　　　　　　.　　　　　　　　　　　　　　　* 　　   　　　　　 ✦ 　　　　　　　         　        　　　　 　　 　　　　　　　 　　　　　.　　　　　　　　　　　　　　　　　　.　　　　　    　　. 　 　　　　　.　　　　 🌑 　　　　　   　　　　　.　　　　　　　　　　　.　　　　　　　　　　   　\n\n　˚　　　　　　　　　　　　　　　　　　　　　ﾟ　　　　　.　　　　　　　　　　　　　　　. 　　 　 🌎 ‍ ‍ ‍ ‍ ‍ ‍ ‍ ‍ ‍ ‍ ,　 　　　　　　　　　　　　　　* .　　　　　 　　　　　　　　　　　　　　.　　　　　　　　　　 ✦ 　　　　   　 　　　˚　　　　　　　　　　　　　　*　　　　　　   　　　　　　　　　　　　　　　.　　　　　　　　　　　　　　.")
    
    @commands.command()
    @commands.check(isnotThreat)
    async def textToEmoji(self, ctx, *, text):
        '''
        Converts text to emoji
        '''
        await ctx.send(textToEmoji(text))

    @commands.command()
    @commands.check(isnotThreat)
    async def emojiToText(self, ctx, *, text):
        '''
        Converts emoji to text
        '''
        await ctx.send(emojiToText(text))

    @commands.command()
    @commands.check(isnotThreat)
    async def surprise(self, ctx: commands.Context):
        '''
        Originally by Kevinozoid
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
        by Kevinozoid.
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
        Detects bad.
        By Kevinozoid
        '''
        if (ctx.author== await (extractUser(ctx,"itchono"))):
            await ctx.send("you are in fact bad")
        else:
            await ctx.send("you are in fact non-bad")

    @commands.command()
    @commands.check(isnotThreat)
    async def quiz(self, ctx: commands.Context):
        '''
        Reaction based trivia.
        By Kevinozoid.
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
    @commands.cooldown(2, 3, type=commands.BucketType.user)
    async def on_message(self, message: discord.Message):
        '''
        Emoji call listener
        '''
        if isnotThreat(await self.bot.get_context(message)):
            if message.content.lower()[0:3] == "tte":
                await self.textToEmoji(await self.bot.get_context(message), text=message.content.lower().lstrip("tte "))
            elif message.content.lower()[0:3] == "ett":
                await self.emojiToText(await self.bot.get_context(message), text=message.content.lower().lstrip("ett "))

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


