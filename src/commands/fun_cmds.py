from utils.utilities import *
from utils.mongo_interface import *

import urllib.request
from bs4 import BeautifulSoup

import numpy as np
from numpy import log, log10, log1p, log2, logaddexp, logaddexp2, exp, exp2, sqrt, power, e, pi, sin, cos,tan,arcsin,arccos,arctan,arcsinh,arccosh,arctan2,radians,rad2deg,deg2rad,radians,sinc,sinh,tanh,angle

import matplotlib.pyplot as plt
import parser
import io

import re

class Fun(commands.Cog):
    '''
    Fun stuff.
    '''
    def __init__(self, bot):
        self.bot = bot
        self.activetrivia = {}

        self.activeGuess = None
        self.guessState = False
        self.streak = {}  # NOTE: Changed to dictionary
        self._last_member = None

    @commands.command()
    async def graph(self, ctx: commands.Context, function: str, xstart: int = -10, xend: int = 10):
        '''
        Graphs a single variable algebraic function in some domain.
        '''
        async with ctx.channel.typing():
            if "." in function:
                await ctx.send("Function rejected for invalid syntax.")
            else:
                function = re.sub(r"([0-9])([a-z])", r"\1*\2", function)
                function = function.replace("^", "**") # exponentiation

                stepsize = 500
                try:
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

                except:
                    await ctx.send("Something went wrong with parsing. Try again.")


    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.channel)
    async def space(self, ctx: commands.Context):
        '''
        Posts text with stars and space. Best used on dark theme.
        '''

        space = ".　　　　　　　　　　 ✦ 　　　　   　 　　　˚　　　　　　　　　　　　　　*　　　　　　   　　　　　　　　　　　　　　　.　　　　　　　　　　　　　　. 　　 　　　　　　　 ✦ 　　　　　　　　　　 　 ‍ ‍ ‍ ‍ 　　　　 　　　　　　　　　　　　,　　   　.　　　　　　　　　　　　　.　　　ﾟ　  　　　.　　　　　　　　　　　　　.　　　　　　,　　　　　　　.　　　　　　    　　　　 　　　　　　　　　　　　　　　　　　 ☀️ 　　　　　　　　　　　　　　　　　　    　      　　　　　        　　　　　　　　　　　　　. 　　　　　　　　　　.　　　　　　　　　　　　　. 　　　　　　　　　　　　　　　　       　   　　　　 　　　　　　　　　　　　　　　　       　   　　　　　　　　　　　　　　　　       　    ✦ 　   　　　,　　　　　　　　　　　     　　　　 　　,　　　 ‍ ‍ ‍ ‍ 　 　　　　　　　　　　　　.　　　　　 　　 　　　.　　　　　　　　　　　　　 　           　　　　　　　　　　　　　　　　　　　˚　　　 　   　　　　,　　　　　　　　　　　       　    　　　　　　　　　　　　　　　　.　　　  　　    　　　　　 　　　　　.　　　　　　　　　　　　　.　　　　　　　　　　　　　　　* 　　   　　　　　 ✦ 　　　　　　　         　        　　　　 　　 　　　　　　　 　　　　　.　　　　　　　　　　　　　　　　　　.　　　　　    　　. 　 　　　　　.　　　　 🌑 　　　　　   　　　　　.　　　　　　　　　　　.　　　　　　　　　　   　　˚　　　　　　　　　　　　　　　　　　　　　ﾟ　　　　　.　　　　　　　　　　　　　　　. 　　 　 🌎 ‍ ‍ ‍ ‍ ‍ ‍ ‍ ‍ ‍ ‍ ,　 　　　　　　　　　　　　　　* .　　　　　 　　　　　　　　　　　　　　.　　　　　　　　　　 ✦ 　　　　   　 　　　˚　　　　　　　　　　　　　　*　　　　　　   　　　　　　　　　　　　　　　.　　　　　　　　　　　　　　."

        m = await ctx.send(space)
    
        for i in range(0, len(space), 3):
            space = space[i:] + space[:i]
            
            await asyncio.sleep(1)
            await m.edit(content = space)
            

    @commands.command()
    @commands.check(isNotThreat())
    async def textToEmoji(self, ctx: commands.Context, *, text):
        '''
        Converts text to emoji
        '''
        await ctx.send(textToEmoji(text))

    @commands.command()
    @commands.check(isNotThreat())
    async def emojiToText(self, ctx: commands.Context, *, text):
        '''
        Converts emoji to text
        '''
        await ctx.send(emojiToText(text))
           
    @commands.command()
    @commands.check(isNotThreat())
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

        if len(holyText > 10000):
            holyText = holyText[0:10000]
            await ctx.send("Text was trimmed to first 10000 characters for being too long.")

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
    @commands.check(isNotThreat())
    async def detectBad(self, ctx: commands.Context):
        '''
        Detects bad.
        By Kevinozoid
        '''
        if (ctx.author== await (extractUser(ctx,"itchono"))): await ctx.send("you are in fact bad")
        else: await ctx.send("you are in fact non-bad")

    @commands.command()
    @commands.guild_only()
    async def random(self, ctx : commands.Context, channel : discord.TextChannel):
        '''
        Gets a random image from the last 1000 messages in a channel
        '''
        async with ctx.channel.typing():
            messages = [i.attachments[0].url for i in await channel.history(limit=2000).flatten() if len(i.attachments) > 0]
            if len(messages) > 0:
                embed = discord.Embed()
                embed.set_image(url=random.choice(messages))
                await ctx.send(embed=embed)
            else:
                await ctx.send("No suitable images were found : (")

    @commands.command()
    @commands.check(isNotThreat())
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
                self.activetrivia[m.id] = "1️⃣"
            elif " B" in questions[element+counter+1] or " B" in questions[element+counter+2]:
                self.activetrivia[m.id] = "2️⃣"
            elif " C" in questions[element+counter+1] or " C" in questions[element+counter+2]:
                self.activetrivia[m.id] = "3️⃣"
            elif " D" in questions[element+counter+1] or " D" in questions[element+counter+2]:
               self.activetrivia[m.id] = "4️⃣"
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
                await ctx.send("Quiz ended because no one answered.")

    @commands.command()
    @commands.check(isOP)
    @commands.guild_only()
    async def timestop(self, ctx:commands.Context, time:int=5, exemptdaily=False):
        '''
        Stops time.

        TODO permissions for daily_roled
        '''
        embed = discord.Embed(title="ZA WARUDO", colour=discord.Colour.from_rgb(*THEME_COLOUR))
        embed.set_image(url=("https://media1.tenor.com/images/4b953bf5b5ba531099a823944a5626c2/tenor.gif"))

        await ctx.send(embed=embed, delete_after=1.95)

        permsOG = ctx.channel.overwrites_for(ctx.guild.default_role)
        permsNEW = discord.PermissionOverwrite.from_pair(*permsOG.pair())
        permsNEW.send_messages = False

        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=permsNEW)

        if exemptdaily:
            dailyrole = await dailyRole(ctx.guild)
            permsOGDaily = ctx.channel.overwrites_for(dailyrole)
            permsNEWDaily = discord.PermissionOverwrite.from_pair(*permsOGDaily.pair())
            permsNEWDaily.send_messages = True
            await ctx.channel.set_permissions(dailyrole, overwrite=permsNEWDaily)

        await asyncio.sleep(1.95)
        
        mt = await ctx.send("*Time is frozen*")

        # fun counter thing
        if int(time) <= 20:
            for i in range(int(time)):
                await asyncio.sleep(1)
                t = i+1
                if t == 1: await mt.edit(content="1 second has passed", suppress=False)
                else: await mt.edit(content="{} seconds have passed".format(t), suppress=False)

        else: await asyncio.sleep(int(time)-2 if int(time) >= 2 else 0)

        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=permsOG)

        if exemptdaily: await ctx.channel.set_permissions(dailyrole, overwrite=None if permsOGDaily.is_empty() else permsOGDaily)

        await mt.edit(content="*Time has begun to move again.*", suppress=False)

        #await log(ctx.guild, "ZA HANDO in {}".format(ctx.channel.name)) TODO FIX


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        '''
        Emoji call listener
        Also guess checker implemented for use in the guessing minigame
        '''
        if isNotThreat()(await self.bot.get_context(message)):
            # Emoji converters
            if message.content.lower()[0:3] == "tte":
                await self.textToEmoji(await self.bot.get_context(message), text=message.content.lower().lstrip("tte "))
            elif message.content.lower()[0:3] == "ett":
                await self.emojiToText(await self.bot.get_context(message), text=message.content.lower().lstrip("ett "))

        if message.author != self.bot.user:
            if message.content == "STAR PLATINUM" and isNotThreat(1)(await self.bot.get_context(message)):
                await self.timestop(await self.bot.get_context(message), 5, True)
            elif message.content == "STAR PLATINUM":
                await message.channel.send("You are unworthy to use the power of a stand!")


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:discord.Reaction, user:discord.User):
        '''
        When a user adds a reaction to a message.
        '''
        m = reaction.message

        checker = self.bot.user in await reaction.users().flatten() # validates that the reponse comes from the bot

        if reaction.message.author == self.bot.user and checker and user != self.bot.user and reaction.emoji in {"1️⃣", "2️⃣", "3️⃣", "4️⃣"}:
            await reaction.message.add_reaction({True:"☑", False:"🅱"}[reaction.emoji ==  self.activetrivia[m.id]])
            await reaction.message.channel.send(user.mention + {True:" CORRECT", False:" WRONG"}[reaction.emoji ==  self.activetrivia[m.id]])
                
    @commands.command()
    @commands.guild_only()
    async def guessStats(self, ctx: commands.Context):
        '''
        Stats for guess
        '''

        highscore = 0
        currscore = 0

        try: highscore = getUser(ctx.author.id, ctx.guild.id)["highest guess streak"]
        except: pass

        try: currscore = self.streak[ctx.author.id]
        except: pass

        await ctx.send(f"**Info for {ctx.author.display_name}**\nCurrent Streak: {currscore}\nHighest Streak: {highscore}")

    @commands.command()
    @commands.guild_only()
    async def guess(self, ctx: commands.Context, *, guess=None):
        '''
        Guessing game
        By Phtephen99 with help from Itchono, with the power of friendship and other ppl's funtions
        we created a minigame which uses the n-gram model built by Itchono where users guess who the generated
        text was based off of. 
        '''

        #TODO
        '''
        - Generate a random user (done)
        - Generate some text (done)
        - Expand game (in progress)
            - Streaks(in progress)
                - Make the framework(done)
                - Integrate streaks into mongoDb database as a field for the user(in progress)
            - Powerups(in progress)
            - Better UX and UI(future plans)
            - Leaderboards(future plans)
        - Optimize code(In progress)
        '''

        if guess and self.guessState:
            streakPrompts = {
                3 : "guessing spree!",
                4 : "rampage!",
                5 : "unstoppable!",
                6 : "godlike!",
                7 : "legendary!",
                8 : "umm Insane?",
                9 : "... how?",
                10: "this is getting kinda creepy ngl.",
                11: "reaching the current max for normal streak prompts, continue to accumulate your streak to unlock bonus prompts!",
                69: "has just won at life!",
                420: "suuuuuuuhhhhhh *puffs out giant cloud of smoke.",
                9999: "\nIf someone reaches this, good job, you have earned my respect - Stephen Luu June 13, 2020."
            }

            if u := await extractUser(ctx, guess):
                if u.display_name == self.activeGuess:
                    out = "Congratulations you gave guessed right!"
                    self.guessState = False 

                    try:
                        self.streak[ctx.author.id] += 1
                        if self.streak[ctx.author.id] >= 3:
                            if self.streak[ctx.author.id] <= 4:
                                out += f"\n**{ctx.author.display_name} is on a {streakPrompts[self.streak[ctx.author.id]]} Streak: {self.streak[ctx.author.id]}**"
                            elif self.streak[ctx.author.id] in streakPrompts:
                                out += f"\n**{ctx.author.display_name} is {streakPrompts[self.streak[ctx.author.id]]} Streak: {self.streak[ctx.author.id]}**"
                    except:
                        self.streak[ctx.author.id] = 1

                    await ctx.send(out)

                    udict = getUser(ctx.author.id, ctx.guild.id)
                    try:
                        if self.streak[ctx.author.id] > udict["highest guess streak"]:
                            udict["highest guess streak"] = self.streak[ctx.author.id]
                            
                    except: 
                        udict["highest guess streak"] = self.streak[ctx.author.id]

                    updateUser(udict)

                    await ctx.send(f"{ctx.author.mention} has achieved a new high score: {self.streak[ctx.author.id]}")

                else:
                    self.guessState = False
                    out = f"\nYikes that was incorrect, it was {self.activeGuess}."

                    try:
                        if self.streak[ctx.author.id] >= 3:
                            out += f"\n**OOOOOF {ctx.author.display_name}'s streak got reset back to 0 from {self.streak[ctx.author.id]}**"
                    except: pass
                    self.streak[ctx.author.id] = 0
                    await ctx.send(out)

        elif not self.guessState and guess:
            await ctx.send(f"No prompt, try entering `{BOT_PREFIX}guess` to generate a prompt")

        elif self.guessState and not guess:
            await ctx.send("There's already a prompt, try guessing for that one before asking for another prompt.")

        elif not self.guessState and not guess:
            await ctx.trigger_typing()
            NUMBER = 20 # number of tokens to make
            text_gen_module = self.bot.get_cog("Polymorph")
            user_cmds = self.bot.get_cog("Users")


            if ctx.guild.id in user_cmds.UNWEIGHTED_RND_USER:  
                pool = user_cmds.UNWEIGHTED_RND_USER[ctx.guild.id]

                txt = None

                while not txt:
                    luckyperson = random.choice(pool) # user object that we can directly call upon for all Discord functions
                    #print(luckyperson.display_name.encode("UTF-8")) #Debugging print, TODO get rid when fully deployed
                    try:
                        model = text_gen_module.models[(luckyperson.id, ctx.guild.id)]
                        txt = text(model, NUMBER)
                    except:
                        await text_gen_module.buildModel(ctx, luckyperson.mention, silent=True)
                        try:
                            model = text_gen_module.models[(luckyperson.id, ctx.guild.id)]
                            txt = text(model, NUMBER)
                        except:
                            pass

                self.activeGuess = luckyperson.display_name
                await ctx.send(f'Who could have typed this? Submit your guess using `{BOT_PREFIX}guess <your guess>`\n```{txt}```')
                self.guessState = True
            else:
                await ctx.send("The user cache is not loaded yet. Give it a few seconds and try again.")




