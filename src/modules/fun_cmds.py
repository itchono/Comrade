import discord
from discord.ext import commands
from utils import *

from utils.additional.emoji_converter import *
from polymorph import *

import urllib.request, asyncio, random
from bs4 import BeautifulSoup

class Fun(commands.Cog):
    '''
    Fun stuff.
    '''
    def __init__(self, bot):
        self.bot = bot

        self.activeGuess = None
        self.guessState = False
        self.streak = {}  # NOTE: Changed to dictionary


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
    async def fanfic(self,ctx: commands.Context,*, site):
        '''
        initiate fanfiction
        by Kevinozoid.
        '''
        await ctx.trigger_typing()

        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,}

        request = urllib.request.Request(site,None,headers)
        req = urllib.request.urlopen(request)
        html = req.read()
        soup = BeautifulSoup(html, features="html.parser")

        for script in soup(["script", "style"]): script.extract() 

        holyText = soup.get_text()

        if len(holyText) > 10000:
            holyText = holyText[:10000]
            await ctx.send("Text was trimmed to first 10000 characters for being too long.")

        paginator = commands.Paginator(prefix="", suffix="")

        lines = holyText.splitlines()

        lines = [lines[i] for i in range(len(lines))]

        for line in lines: paginator.add_line(line)

        for page in paginator.pages: await ctx.send(page); await asyncio.sleep(1)
        await ctx.send("**<END OF TEXT>**")

    @commands.command()
    @commands.check(isNotThreat())
    async def detectBad(self, ctx: commands.Context):
        '''
        Detects bad.
        By Kevinozoid
        '''
        if (ctx.author== await (getUser(ctx,"itchono"))): await ctx.send("you are in fact bad")
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
        checkboi = [1]
        req = urllib.request.urlopen("https://pastebin.com/raw/2PjhRjtn", timeout = 10)
        questions = req.read().decode().splitlines()
        questions.remove("")
        while checkboi:
            count = 0
            random.seed()
            checkboi.pop()
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
                answer = "1️⃣"
            elif " B" in questions[element+counter+1] or " B" in questions[element+counter+2]:
                answer = "2️⃣"
            elif " C" in questions[element+counter+1] or " C" in questions[element+counter+2]:
                answer = "3️⃣"
            elif " D" in questions[element+counter+1] or " D" in questions[element+counter+2]:
                answer = "4️⃣"
            else:
                await ctx.send("SOMETHING BROKE")

            await m.add_reaction("1️⃣")
            await m.add_reaction("2️⃣")
            await m.add_reaction("3️⃣")
            await m.add_reaction("4️⃣")

            async def capturereacts():

                while 1:

                    def checker(reaction, user): return reaction.message.author == self.bot.user and user != self.bot.user
                    
                    reaction, user = await self.bot.wait_for("reaction_add", check=checker, timeout = count)

                    if self.bot.user in await reaction.users().flatten() and reaction.emoji in {"1️⃣", "2️⃣", "3️⃣", "4️⃣"}:
                        checkboi.append(1)
                        try:
                            await reaction.message.add_reaction({True:"☑", False:"🅱"}[reaction.emoji == answer])
                            await reaction.message.channel.send(user.mention + {True:" CORRECT", False:" WRONG"}[reaction.emoji == answer])
                        except: pass
                        
            
            try: await capturereacts()
            except asyncio.TimeoutError:
                await m.remove_reaction("1️⃣", self.bot.user)
                await m.remove_reaction("2️⃣", self.bot.user)
                await m.remove_reaction("3️⃣", self.bot.user)
                await m.remove_reaction("4️⃣", self.bot.user)

                if checkboi: continue
                else: await ctx.send("Quiz ended because no one answered.")

    @commands.command()
    @commands.check(isOP)
    @commands.guild_only()
    async def timestop(self, ctx:commands.Context, time:int=5, exemptdaily=False):
        '''
        Stops time.
        '''
        embed = discord.Embed(title="ZA WARUDO", colour=discord.Colour.from_rgb(*DBcfgitem(ctx.guild.id,"theme-colour")))
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
        await utils.utilities.log(ctx.guild, f"Timestop in {ctx.channel.mention} lasting {time} seconds, performed by {ctx.author.mention}")
        

        


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

                
    @commands.command()
    @commands.guild_only()
    async def guessStats(self, ctx: commands.Context):
        '''
        Stats for guess
        '''

        highscore = DBuser(ctx.author.id, ctx.guild.id)["highest-guess-streak"]
        currscore = self.streak[ctx.author.id]

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

            if u := await getUser(ctx, guess):
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

                    udict = DBuser(ctx.author.id, ctx.guild.id)
                    try:
                        if self.streak[ctx.author.id] > udict["highest-guess-streak"]:
                            udict["highest-guess-streak"] = self.streak[ctx.author.id]
                            
                    except: 
                        udict["highest-guess-streak"] = self.streak[ctx.author.id]

                    updateDBuser(udict)

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

    @commands.command()
    async def defaultdance(self, ctx: commands.Context):
        '''
        posts important copypasta
        '''

        await ctx.send("```⠀⠀⠀⠀⣀⣤\n⠀⠀⠀⠀⣿⠿⣶\n⠀⠀⠀⠀⣿⣿⣀\n⠀⠀⠀⣶⣶⣿⠿⠛⣶\n⠤⣀⠛⣿⣿⣿⣿⣿⣿⣭⣿⣤\n⠒⠀⠀⠀⠉⣿⣿⣿⣿⠀⠀⠉⣀\n⠀⠤⣤⣤⣀⣿⣿⣿⣿⣀⠀⠀⣿\n⠀⠀⠛⣿⣿⣿⣿⣿⣿⣿⣭⣶⠉\n⠀⠀⠀⠤⣿⣿⣿⣿⣿⣿⣿\n⠀⠀⠀⣭⣿⣿⣿⠀⣿⣿⣿\n⠀⠀⠀⣉⣿⣿⠿⠀⠿⣿⣿\n⠀⠀⠀⠀⣿⣿⠀⠀⠀⣿⣿⣤\n⠀⠀⠀⣀⣿⣿⠀⠀⠀⣿⣿⣿\n⠀⠀⠀⣿⣿⣿⠀⠀⠀⣿⣿⣿\n⠀⠀⠀⣿⣿⠛⠀⠀⠀⠉⣿⣿\n⠀⠀⠀⠉⣿⠀⠀⠀⠀⠀⠛⣿\n⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⣿⣿\n⠀⠀⠀⠀⣛⠀⠀⠀⠀⠀⠀⠛⠿⠿⠿\n⠀⠀⠀⠛⠛```")
        await asyncio.sleep(1)
        await ctx.send("```⠀⠀⠀⣀⣶⣀\n⠀⠀⠀⠒⣛⣭\n⠀⠀⠀⣀⠿⣿⣶\n⠀⣤⣿⠤⣭⣿⣿\n⣤⣿⣿⣿⠛⣿⣿⠀⣀\n⠀⣀⠤⣿⣿⣶⣤⣒⣛\n⠉⠀⣀⣿⣿⣿⣿⣭⠉\n⠀⠀⣭⣿⣿⠿⠿⣿\n⠀⣶⣿⣿⠛⠀⣿⣿\n⣤⣿⣿⠉⠤⣿⣿⠿\n⣿⣿⠛⠀⠿⣿⣿\n⣿⣿⣤⠀⣿⣿⠿\n⠀⣿⣿⣶⠀⣿⣿⣶\n⠀⠀⠛⣿⠀⠿⣿⣿\n⠀⠀⠀⣉⣿⠀⣿⣿\n⠀⠶⣶⠿⠛⠀⠉⣿\n⠀⠀⠀⠀⠀⠀⣀⣿\n⠀⠀⠀⠀⠀⣶⣿⠿```")
        await asyncio.sleep(1)
        await ctx.send("```⠀⠀⠀⠀⠀⠀⠀⠀⣤⣿⣿⠶⠀⠀⣀⣀\n⠀⠀⠀⠀⠀⠀⣀⣀⣤⣤⣶⣿⣿⣿⣿⣿⣿\n⠀⠀⣀⣶⣤⣤⠿⠶⠿⠿⠿⣿⣿⣿⣉⣿⣿\n⠿⣉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⣤⣿⣿⣿⣀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿⣶⣤\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣿⣿⣿⣿⠿⣛⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⠛⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⣿⣿⠿⠀⣿⣿⣿⠛\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⠀⠀⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⠿⣿⠀⠀⣿⣶\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠛⠀⠀⣿⣿⣶\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⠤\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⣿```")
        await asyncio.sleep(1)
        await ctx.send("```⠀⠀⣀\n⠀⠿⣿⣿⣀\n⠀⠉⣿⣿⣀\n⠀⠀⠛⣿⣭⣀⣀⣤\n⠀⠀⣿⣿⣿⣿⣿⠛⠿⣶⣀\n⠀⣿⣿⣿⣿⣿⣿⠀⠀⠀⣉⣶\n⠀⠀⠉⣿⣿⣿⣿⣀⠀⠀⣿⠉\n⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿\n⠀⣀⣿⣿⣿⣿⣿⣿⣿⣿⠿\n⠀⣿⣿⣿⠿⠉⣿⣿⣿⣿\n⠀⣿⣿⠿⠀⠀⣿⣿⣿⣿\n⣶⣿⣿⠀⠀⠀⠀⣿⣿⣿\n⠛⣿⣿⣀⠀⠀⠀⣿⣿⣿⣿⣶⣀\n⠀⣿⣿⠉⠀⠀⠀⠉⠉⠉⠛⠛⠿⣿⣶\n⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣿\n⠀⠀⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉\n⣀⣶⣿⠛```")    
        await asyncio.sleep(1)
        await ctx.send("```⠀⠀⠀⠀⠀⠀⠀⣀⣀\n⠀⠀⠀⠀⠀⠀⣿⣿⣿⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣤⣿\n⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣶⣿⣿⣿⣶⣶⣤⣶⣶⠶⠛⠉⠉\n⠀⠀⠀⠀⠀⠀⣤⣿⠿⣿⣿⣿⣿⣿⠀⠀⠉\n⠛⣿⣤⣤⣀⣤⠿⠉⠀⠉⣿⣿⣿⣿\n⠀⠉⠉⠉⠉⠉⠀⠀⠀⠀⠉⣿⣿⣿⣀\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣶⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⠛\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣛⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⣶⣿⣿⠛⠿⣿⣿⣿⣶⣤\n⠀⠀⠀⠀⠀⠀⠀⣿⠛⠉⠀⠀⠀⠛⠿⣿⣿⣶⣀\n⠀⠀⠀⠀⠀⠀⣿⣀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠛⠿⣶⣤\n⠀⠀⠀⠀⠀⠛⠿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣿⣿⠿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠛⠉⠉```")
        await asyncio.sleep(1)
        await ctx.send("```⠀⠀⠀⠀⠀⠀⣤⣶⣶\n⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣀⣀\n⠀⠀⠀⠀⠀⣀⣶⣿⣿⣿⣿⣿⣿\n⣤⣶⣀⠿⠶⣿⣿⣿⠿⣿⣿⣿⣿\n⠉⠿⣿⣿⠿⠛⠉⠀⣿⣿⣿⣿⣿\n⠀⠀⠉⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣤⣤\n⠀⠀⠀⠀⠀⠀⠀⣤⣶⣿⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⣀⣿⣿⣿⣿⣿⠿⣿⣿⣿⣿\n⠀⠀⠀⠀⣀⣿⣿⣿⠿⠉⠀⠀⣿⣿⣿⣿\n⠀⠀⠀⠀⣿⣿⠿⠉⠀⠀⠀⠀⠿⣿⣿⠛\n⠀⠀⠀⠀⠛⣿⣿⣀⠀⠀⠀⠀⠀⣿⣿⣀\n⠀⠀⠀⠀⠀⣿⣿⣿⠀⠀⠀⠀⠀⠿⣿⣿\n⠀⠀⠀⠀⠀⠉⣿⣿⠀⠀⠀⠀⠀⠀⠉⣿\n⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⣀⣿\n⠀⠀⠀⠀⠀⠀⣀⣿⣿\n⠀⠀⠀⠀⠤⣿⠿⠿⠿```")
        await asyncio.sleep(1)
        await ctx.send("```⠀⠀⠀⠀⣀\n⠀⠀⣶⣿⠿⠀⠀⠀⣀⠀⣤⣤\n⠀⣶⣿⠀⠀⠀⠀⣿⣿⣿⠛⠛⠿⣤⣀\n⣶⣿⣤⣤⣤⣤⣤⣿⣿⣿⣀⣤⣶⣭⣿⣶⣀\n⠉⠉⠉⠛⠛⠿⣿⣿⣿⣿⣿⣿⣿⠛⠛⠿⠿\n⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⠿\n⠀⠀⠀⠀⠀⠀⠀⠿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⣭⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⣤⣿⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⠿\n⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⠿\n⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⣿⠛⠿⣿⣤\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣿⠀⠀⠀⣿⣿⣤\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠀⠀⠀⣶⣿⠛⠉\n⠀⠀⠀⠀⠀⠀⠀⠀⣤⣿⣿⠀⠀⠉\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉```")
        await asyncio.sleep(1)
        await ctx.send("```⠀⠀⠀⠀⠀⠀⣶⣿⣶\n⠀⠀⠀⣤⣤⣤⣿⣿⣿\n⠀⠀⣶⣿⣿⣿⣿⣿⣿⣿⣶\n⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⣿\n⠀⠀⣿⣉⣿⣿⣿⣿⣉⠉⣿⣶\n⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⠿⣿\n⠀⣤⣿⣿⣿⣿⣿⣿⣿⠿⠀⣿⣶\n⣤⣿⠿⣿⣿⣿⣿⣿⠿⠀⠀⣿⣿⣤\n⠉⠉⠀⣿⣿⣿⣿⣿⠀⠀⠒⠛⠿⠿⠿\n⠀⠀⠀⠉⣿⣿⣿⠀⠀⠀⠀⠀⠀⠉\n⠀⠀⠀⣿⣿⣿⣿⣿⣶\n⠀⠀⠀⠀⣿⠉⠿⣿⣿\n⠀⠀⠀⠀⣿⣤⠀⠛⣿⣿\n⠀⠀⠀⠀⣶⣿⠀⠀⠀⣿⣶\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣭⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⣤⣿⣿⠉```")
        await asyncio.sleep(1)
        await ctx.send("```⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣶\n⠀⠀⠀⠀⠀⣀⣀⠀⣶⣿⣿⠶\n⣶⣿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣤⣤\n⠀⠉⠶⣶⣀⣿⣿⣿⣿⣿⣿⣿⠿⣿⣤⣀\n⠀⠀⠀⣿⣿⠿⠉⣿⣿⣿⣿⣭⠀⠶⠿⠿\n⠀⠀⠛⠛⠿⠀⠀⣿⣿⣿⣉⠿⣿⠶\n⠀⠀⠀⠀⠀⣤⣶⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿⣿⣿⠒\n⠀⠀⠀⠀⣀⣿⣿⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⣿⣿⣿⠛⣭⣭⠉\n⠀⠀⠀⠀⠀⣿⣿⣭⣤⣿⠛\n⠀⠀⠀⠀⠀⠛⠿⣿⣿⣿⣭\n⠀⠀⠀⠀⠀⠀⠀⣿⣿⠉⠛⠿⣶⣤\n⠀⠀⠀⠀⠀⠀⣀⣿⠀⠀⣶⣶⠿⠿⠿\n⠀⠀⠀⠀⠀⠀⣿⠛\n⠀⠀⠀⠀⠀⠀⣭⣶```")
        await asyncio.sleep(1)
        await ctx.send("```⠀⠀⠀⠀⠀⠀⠀⠀⠀⣤⣤\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿\n⠀⠀⣶⠀⠀⣀⣤⣶⣤⣉⣿⣿⣤⣀\n⠤⣤⣿⣤⣿⠿⠿⣿⣿⣿⣿⣿⣿⣿⣿⣀\n⠀⠛⠿⠀⠀⠀⠀⠉⣿⣿⣿⣿⣿⠉⠛⠿⣿⣤\n⠀⠀⠀⠀⠀⠀⠀⠀⠿⣿⣿⣿⠛⠀⠀⠀⣶⠿\n⠀⠀⠀⠀⠀⠀⠀⠀⣀⣿⣿⣿⣿⣤⠀⣿⠿\n⠀⠀⠀⠀⠀⠀⠀⣶⣿⣿⣿⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠿⣿⣿⣿⣿⣿⠿⠉⠉\n⠀⠀⠀⠀⠀⠀⠀⠉⣿⣿⣿⣿⠿\n⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⠉\n⠀⠀⠀⠀⠀⠀⠀⠀⣛⣿⣭⣶⣀\n⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠉⠛⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠀⠀⣿⣿\n⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣉⠀⣶⠿\n⠀⠀⠀⠀⠀⠀⠀⠀⣶⣿⠿\n⠀⠀⠀⠀⠀⠀⠀⠛⠿⠛```")
        await asyncio.sleep(1)
        await ctx.send("```⠀⠀⠀⣶⣿⣶\n⠀⠀⠀⣿⣿⣿⣀\n⠀⣀⣿⣿⣿⣿⣿⣿\n⣶⣿⠛⣭⣿⣿⣿⣿\n⠛⠛⠛⣿⣿⣿⣿⠿\n⠀⠀⠀⠀⣿⣿⣿\n⠀⠀⣀⣭⣿⣿⣿⣿⣀\n⠀⠤⣿⣿⣿⣿⣿⣿⠉\n⠀⣿⣿⣿⣿⣿⣿⠉\n⣿⣿⣿⣿⣿⣿\n⣿⣿⣶⣿⣿\n⠉⠛⣿⣿⣶⣤\n⠀⠀⠉⠿⣿⣿⣤\n⠀⠀⣀⣤⣿⣿⣿\n⠀⠒⠿⠛⠉⠿⣿\n⠀⠀⠀⠀⠀⣀⣿⣿\n⠀⠀⠀⠀⣶⠿⠿⠛ ```")

    #owo
    def konoesubaru (self, t):
        remove_characters = ["R", "L", "r", "l"]
        for character in remove_characters:
            if character.islower():
                t = t.replace(character, "w")
            else:
                t = t.replace(character, "W")
        return t

    @commands.command()
    async def owoify(self, ctx: commands.Context, *, text:str = ""):
        '''
        changes all R's and L's to W's
        '''
        t = text.strip()      
        
        if len(t) == 0:
            #owoify previous message
            msg = (await ctx.channel.history(limit=2).flatten())[1]
            auth = msg.author
            t = msg.content
        else:
            auth = ctx.author

        c = self.bot.get_cog("Echo")
        await c.extecho(ctx, self.konoesubaru(t), str(auth.name), deleteMsg=False)

    #emojify
    def tokisakikurumi (self, ctx, t):
        return "".join([str(random.choice(ctx.guild.emojis)) if s == " " else s for s in t])

    @commands.command()
    async def emojify (self, ctx: commands.Context, *, text:str = ""):
        '''
        adds random emojis in spaces
        '''
        t = text.strip()
        
        if len(t) == 0:
            msg = (await ctx.channel.history(limit=2).flatten())[1]
            auth = msg.author
            t = msg.content
        else:
            auth = ctx.author

        c = self.bot.get_cog("Echo")
        await c.extecho(ctx, self.tokisakikurumi(ctx, t), str(auth.name), deleteMsg=False)

    #mock
    def nyaruko (self, t):
        s = ""

        for character in t:
            if random.random() < 0.5:
                s += character.lower()
            else:
                s += character.upper()
        return s

    @commands.command()
    async def mock (self, ctx: commands.Context, *, text:str = ""):
        '''
        randomly capitalizes and lowercases a message
        '''

        t = text.strip()

        if len(t) == 0:
            msg = (await ctx.channel.history(limit=2).flatten())[1]
            auth = msg.author
            t = msg.content
        else:
            auth = ctx.author
              
        c = self.bot.get_cog("Echo")
        await c.extecho(ctx, self.nyaruko(t), str(auth.name), deleteMsg=False)

    @commands.command()
    async def fuckup (self, ctx: commands.Context, *, text:str = ""):
        '''
        ruin someone's day
        '''
        t = text.strip()
        if len(t) == 0:
            msg = (await ctx.channel.history(limit=2).flatten())[1]
            auth = msg.author
            t = msg.content
        else:
            auth = ctx.author

        c = self.bot.get_cog("Echo")
        await c.extecho(ctx, self.konoesubaru(self.tokisakikurumi(ctx, self.nyaruko(t))), str(auth.name), deleteMsg=False)

    @commands.command()
    async def futa (self, ctx: commands.Context, m: discord.Message = None):
        '''
        Developed by Futanari Yaoi. Search on Google to learn more about his work
        '''
        
        if not m:
            m = (await ctx.channel.history(limit=2).flatten())[1]

        #spell futanari yaoi
        await m.add_reaction(u"\U0001F1EB")
        await m.add_reaction(u"\U0001F1FA")
        await m.add_reaction(u"\U0001F1F9")
        await m.add_reaction(u"\U0001F1E6")
        await m.add_reaction(u"\U0001F1F3")
        await m.add_reaction("🅰️")
        await m.add_reaction(u"\U0001F1F7")
        await m.add_reaction(u"\U0001F1EE")

        await m.add_reaction("▪️")
        
        await m.add_reaction(u"\U0001F1FE")
        await m.add_reaction("4️⃣")
        await m.add_reaction("0️⃣")
        await m.add_reaction("ℹ️")

        await m.add_reaction("◼️")
        await m.add_reaction("♀️")
        await m.add_reaction("♂️")
        await m.add_reaction("🍆")
        await m.add_reaction("💦")
