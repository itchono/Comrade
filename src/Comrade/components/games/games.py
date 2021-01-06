import discord
from discord.ext import commands

import asyncio
import urllib.request
import random
import typing

from .broken_picture_phone import BPCGame
from .terrestrial import TerrestrialGame
from utils.users import random_member_from_server
from utils.utilities import bot_prefix, ufil
from components.tools.text_gen import generate_text, text_model

from db import collection


class Games(commands.Cog):
    '''
    A bunch of games made by the Comrade team,
    playable using text and Discord reactions.
    '''

    def __init__(self, bot):
        self.bot: commands.Bot = bot

        # BPC
        self.active = False
        self.game = None

        # StephenGame
        self.activeGuess = None
        self.guessState = False
        self.streak = {}  # NOTE: Changed to dictionary

    @commands.group()
    @commands.guild_only()
    async def bpc(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('```=========================\n'
                           'BROKEN PICTURE PHONE v1.0\n==='
                           '======================```\n'
                           f'Do `{bot_prefix}bpc '
                           'start` to start a game!')

    @bpc.command(name="start")
    @commands.guild_only()
    async def bpc_start(self, ctx: commands.Context,
                        members: commands.Greedy[discord.Member]):
        '''
        Starts a game of Broken Picture Phone.
        '''
        if len(members) < 2:
            await ctx.send("Sorry, we need at least 2 players to start!")
        else:
            self.game = BPCGame(members, ctx, self.bot)

            print(self.game)

            await ctx.send(str(self.game))

            await self.game.start()

    @commands.group()
    @commands.guild_only()
    async def terrestrial(self, ctx: commands.Context):
        if ctx.invoked_subcommand is None:
            await ctx.send('```=========================\n'
                           '⛏ TERRESTRIAL ⛏ v1.0\n==='
                           '======================```\n'
                           f'Do `{bot_prefix}terrestrial '
                           'start` to start a game!')

    @terrestrial.command(name="start")
    async def terrestrial_start(self, ctx: commands.Context, seed: int = 0):
        '''
        Starts a game of terrestrial
        '''
        game = TerrestrialGame()

        intro_splash = "`Terrestrial v1 -- use arrow reactions to move, use ⛏ to transform into mining mode, use 🛑 to stop."

        m = await ctx.send(game.rendered + game.describe)

        for r in ["⬅", "➡", "⬆", "⬇", "⛏", "🛑"]:
            await m.add_reaction(r)

        def check(reaction, user):
            return str(reaction) in [
                "⬅",
                "➡",
                "⬆",
                "⬇",
                "⛏",
                "🛑"] and user == ctx.author and reaction.message.id == m.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", check=check, timeout=300)
                # cleans up games after 5 minutes

                await m.remove_reaction(reaction, user)

                if str(reaction) == "🛑":
                    for r in ["⬅", "➡", "⬆", "⬇", "⛏"]:
                        await m.remove_reaction(r, self.bot.user)
                    break

                elif str(reaction) == "⛏":
                    game.action()
                else:
                    game.moveplayer(
                        {"⬅": "LEFT", "➡": "RIGHT", "⬆": "UP", "⬇": "DOWN"}[str(reaction)])

                await m.edit(content=game.rendered + game.describe)

            except asyncio.TimeoutError:
                for r in ["⬅", "➡", "⬆", "⬇", "⛏"]:
                    await m.remove_reaction(r, self.bot.user)
                break

    @commands.command()
    async def quiz(self, ctx: commands.Context):
        '''
        Reaction based trivia.
        By Kevinozoid.
        '''
        checkboi = [1]
        req = urllib.request.urlopen(
            "https://pastebin.com/raw/2PjhRjtn", timeout=10)
        questions = req.read().decode().splitlines()
        questions.remove("")
        while checkboi:
            count = 0
            checkboi.pop()
            element = round(random.random() * (len(questions) - 1))
            while not any(char.isdigit(
            ) for char in questions[element][0:2]) or "." not in questions[element][0:5]:
                element = round(random.random() * (len(questions) - 1))

            m = await ctx.send(questions[element])
            counter = 1
            while not questions[element + counter].find('D)') == 0:
                if not questions[element +
                                 counter] == "" and not questions[element +
                                                                  counter] == " ":
                    await ctx.send(questions[element + counter])
                counter += 1
                count += 1
            await ctx.send(questions[element + counter])

            if " A" in questions[element + counter +
                                 1] or " A" in questions[element + counter + 2]:
                answer = "1️⃣"
            elif " B" in questions[element + counter + 1] or " B" in questions[element + counter + 2]:
                answer = "2️⃣"
            elif " C" in questions[element + counter + 1] or " C" in questions[element + counter + 2]:
                answer = "3️⃣"
            elif " D" in questions[element + counter + 1] or " D" in questions[element + counter + 2]:
                answer = "4️⃣"
            else:
                await ctx.send("SOMETHING BROKE")

            await m.add_reaction("1️⃣")
            await m.add_reaction("2️⃣")
            await m.add_reaction("3️⃣")
            await m.add_reaction("4️⃣")

            async def capturereacts():

                while True:

                    def checker(
                        reaction,
                        user): return reaction.message.author == self.bot.user and user != self.bot.user

                    reaction, user = await self.bot.wait_for("reaction_add", check=checker, timeout=count)

                    if self.bot.user in await reaction.users().flatten() and reaction.emoji in {"1️⃣", "2️⃣", "3️⃣", "4️⃣"}:
                        checkboi.append(1)
                        try:
                            await reaction.message.add_reaction({True: "☑", False: "🅱"}[reaction.emoji == answer])
                            await reaction.message.channel.send(user.mention + {True: " CORRECT", False: " WRONG"}[reaction.emoji == answer])
                        except BaseException:
                            pass

            try:
                await capturereacts()
            except asyncio.TimeoutError:
                await m.remove_reaction("1️⃣", self.bot.user)
                await m.remove_reaction("2️⃣", self.bot.user)
                await m.remove_reaction("3️⃣", self.bot.user)
                await m.remove_reaction("4️⃣", self.bot.user)

                if checkboi:
                    continue
                else:
                    await ctx.send("Quiz ended because no one answered.")

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def guess(self, ctx: commands.Context, guess: typing.Optional[discord.Member]):
        '''
        Guessing game
        By Phtephen99 with help from Itchono, with the power of friendship and other ppl's funtions
        we created a minigame which uses the n-gram model built by Itchono where users guess who the generated
        text was based off of.
        '''

        # TODO
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

        if ctx.invoked_subcommand is None:
            if guess and self.guessState:
                streakPrompts = {
                    3: "guessing spree!",
                    4: "rampage!",
                    5: "unstoppable!",
                    6: "godlike!",
                    7: "legendary!",
                    8: "umm Insane?",
                    9: "... how?",
                    10: "this is getting kinda creepy ngl.",
                    11: "reaching the current max for normal streak prompts, continue to accumulate your streak to unlock bonus prompts!",
                    69: "has just won at life!",
                    420: "suuuuuuuhhhhhh *puffs out giant cloud of smoke.",
                    9999: "\nIf someone reaches this, good job, you have earned my respect - Stephen Luu June 13, 2020."}

                if guess.display_name == self.activeGuess:
                    out = "Congratulations you gave guessed right!"
                    self.guessState = False

                    try:
                        self.streak[ctx.author.id] += 1
                        if self.streak[ctx.author.id] >= 3:
                            if self.streak[ctx.author.id] <= 4:
                                out += f"\n**{ctx.author.display_name} is on a {streakPrompts[self.streak[ctx.author.id]]} Streak: {self.streak[ctx.author.id]}**"
                            elif self.streak[ctx.author.id] in streakPrompts:
                                out += f"\n**{ctx.author.display_name} is {streakPrompts[self.streak[ctx.author.id]]} Streak: {self.streak[ctx.author.id]}**"
                    except BaseException:
                        self.streak[ctx.author.id] = 1

                    await ctx.send(out)

                    udict = collection("users").find_one(
                        ufil(ctx.author))

                    if self.streak[ctx.author.id] > udict["guessing-game"]["highest-streak"]:
                        collection("users").update_one(ufil(ctx.author),
                                                       {"$set": {"guessing-game.highest-streak": self.streak[ctx.author.id]}})

                        await ctx.send(f"{ctx.author.mention} has achieved a new high score: {self.streak[ctx.author.id]}")

                else:
                    self.guessState = False
                    out = f"\nYikes that was incorrect, it was {self.activeGuess}."

                    try:
                        if self.streak[ctx.author.id] >= 3:
                            out += f"\n**OOOOOF {ctx.author.display_name}'s streak got reset back to 0 from {self.streak[ctx.author.id]}**"
                    except BaseException:
                        pass
                    self.streak[ctx.author.id] = 0
                    await ctx.send(out)

            elif not self.guessState and guess:
                await ctx.send(f"No prompt, try entering `{bot_prefix}guess` to generate a prompt")

            elif self.guessState and not guess:
                await ctx.send("There's already a prompt, try guessing for that one before asking for another prompt.")

            elif not self.guessState and not guess:
                await ctx.trigger_typing()

                iterations = 0

                txt = None
                luckyperson = None

                while not txt and iterations < 100:
                    iterations += 1
                    luckyperson: discord.Member = random_member_from_server(
                        ctx.guild.id, require_human=True)
                    # print(luckyperson.display_name.encode("UTF-8"))
                    # #Debugging print, TODO get rid when fully deployed

                    m = await ctx.send(f"Building model (This may take a while)")
                    await ctx.trigger_typing()

                    model = await text_model(ctx.channel.id, luckyperson.id)
                    await m.delete()

                    txt = generate_text(model)

                self.activeGuess = luckyperson.display_name
                await ctx.send(f'Who could have typed this? Submit your guess using `{bot_prefix}guess <your guess>`\n```{txt}```')
                self.guessState = True

    @guess.command()
    @commands.guild_only()
    async def stats(self, ctx: commands.Context):
        '''
        Stats for guess
        '''
        highscore = collection("users").find_one(
            ufil(ctx.author))["guessing-game"]["highest-streak"]
        currscore = self.streak[ctx.author.id]

        await ctx.send(f"**Info for {ctx.author.display_name}**\nCurrent Streak: {currscore}\nHighest Streak: {highscore}")
