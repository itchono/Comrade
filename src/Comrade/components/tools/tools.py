import discord
from discord.ext import commands
import string
import re
import io
import typing
import asyncio
import matplotlib.pyplot as plt
import matplotlib as mpl
from sympy import pretty, sympify
from sympy.parsing.sympy_parser import (implicit_multiplication_application,
                                        factorial_notation, convert_xor,
                                        standard_transformations, parse_expr)

from bs4 import BeautifulSoup
from PyDictionary import PyDictionary
import urllib.request
from utils.utilities import webscrape_header, local_time
from utils.echo import echo
from utils.emoji_converter import textToEmoji
from db import collection

mpl.use('agg')  # Prevent tkinter backend from starting which kills webserver

transformations = standard_transformations + \
    (implicit_multiplication_application,) + (factorial_notation,) + (convert_xor,)

# Define constants for news function
with open("static/news_border.txt", "r", encoding="utf-8") as f:
    BORDER_TOP, ACCENT_BORDER, BORDER_BOTTOM = f.read().splitlines()
    len_border = len(BORDER_TOP)


class Tools(commands.Cog):
    '''
    A set of miscellaneous tools for you to use.
    (News, Dictionary, Math, Poll, Channel Creation)
    '''
    # Can operate entiely outside of a server.

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        mpl.rcParams['mathtext.fontset'] = "cm"  # set to Computer Modern

    @commands.group(invoke_without_command=True)
    async def define(self, ctx: commands.Context, *, word):
        '''
        Defines a word
        '''
        if ctx.invoked_subcommand is None:
            await ctx.trigger_typing()

            dictionary = PyDictionary()

            if (meanings := dictionary.meaning(word)):

                printout = f"**__{string.capwords(word)}__:**\n"

                for wordtype in meanings:
                    defs = meanings[wordtype]
                    printout += f"__{wordtype}__\n"

                    for num, d in enumerate(defs, 1):
                        printout += f"{num}. {d}\n"

                await ctx.send(printout)

            else:
                await ctx.send(f"Definition for `{word}` could not be found.")

    @define.command()
    async def urban(self, ctx: commands.Context, *, word):
        '''
        Defines a word in a dictionary

        Credits to MgWg
        '''
        printout = f"**__{string.capwords(word)}__:**\n"

        await ctx.trigger_typing()

        tags = '%20'.join(word.split(" "))
        url = 'https://www.urbandictionary.com/define.php?term=' + tags

        request = urllib.request.Request(url, None, webscrape_header())

        try:
            response = urllib.request.urlopen(request)
        except Exception:
            await ctx.send("No results found.")
            return

        data = response.read()
        soup = BeautifulSoup(data, 'html.parser')
        # Regex pattern for finding text
        r = r'(?<=<div class\="meaning">)(.*?)(?=<div class\="def-footer">)'
        num_results = re.findall(r, str(soup))

        def_1 = BeautifulSoup(num_results[0], features="html.parser")
        ex = def_1.find_all('div', {'class': 'example'})
        example = BeautifulSoup(str(ex[0]), features="html.parser").get_text()
        index = def_1.get_text().index(example)
        def_1 = def_1.get_text()[:index]

        printout += def_1 + f"\n\n__Example:__\n*{example}*"
        await ctx.send(printout)

    @commands.command()
    async def graph(self, ctx: commands.Context, *, function: str):
        '''
        Graphs a 1 variable algebraic function in some domain.
        Runs on SymPy. Syntax Reference: http://daabzlatex.s3.amazonaws.com/9065616cce623384fe5394eddfea4c52.pdf
        Example: x^2 + 6*x + 9, (x, -10, 10)
        '''
        await ctx.trigger_typing()
        try:
            # implicit multiplication
            function = re.sub(r"([0-9])([a-z])", r"\1*\2", function)
            function = function.replace("^", "**")  # exponentiation
            graph = sympify(
                f"plot({function}, title='Plot Requested by {ctx.author.display_name}', show=False)")

            backend = graph.backend(graph)
            backend.process_series()
            f = io.BytesIO()
            backend.fig.savefig(f, format="png", dpi=300)
            f.seek(0)
            backend.fig.clf()

            await ctx.send(file=discord.File(f, "graph.png"))
        except Exception as ex:
            await ctx.send(f"Error: {ex}")

    @commands.command()
    async def calculate(self, ctx: commands.Context, *, expression: str):
        '''
        Evaluates a mathematical expression and returns the most simplified result.
        Runs on SymPy. Syntax Reference: http://daabzlatex.s3.amazonaws.com/9065616cce623384fe5394eddfea4c52.pdf
        '''
        try:
            exp = parse_expr(expression, transformations=transformations)

            try:
                approx = exp.evalf()
                await ctx.send(f"```{pretty(exp, use_unicode = False)}```= `{approx}`")

            except Exception as ex:
                await ctx.send(f"```{pretty(exp, use_unicode = False)}```")

        except Exception as ex:
            await ctx.send(f"Error: {ex}")

    @commands.command()
    async def tex(self, ctx: commands.Context, *, text):
        '''
        Renders a LaTeX equation.
        '''
        await ctx.trigger_typing()

        L = len(text) if len(text) >= 4 else 4
        S = int(630 / L) - 12  # approx text fit based on expression
        if S < 20:
            S = 20

        # add text
        plt.text(0.5, 0.5, r"$%s$" %
                 text, fontsize=S, ha='center', va='center')

        # hide axes
        fig = plt.gca()
        plt.axis('off')
        fig.axes.get_xaxis().set_visible(False)
        fig.axes.get_yaxis().set_visible(False)

        f = io.BytesIO()
        plt.savefig(f, format="png")
        f.seek(0)
        plt.clf()

        await ctx.send(file=discord.File(f, "renderedtex.png"))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        '''
        Inline calculator
        '''
        if message.content and \
                not message.author.bot and message.content[:2] == "==":
            await self.calculate(
                await self.bot.get_context(message),
                expression=message.content[2:])

    @commands.command()
    async def news(self, ctx: commands.Context, *, content):
        '''
        Wraps a piece of text in a fancy border for news
        '''
        words = content.split(" ")
        lines = []
        buffer = ""  # line buffer

        while words:
            # do until the array of words is empty
            if len(words[0]) >= len_border and (max_word := words.pop(0)):
                words = [max_word[:len_border - 2] + '-',
                         max_word[len_border - 2:]] + words
                # case: word is too long

            while words and len(buffer + words[0]) < len_border:
                buffer += words.pop(0) + " "

            lines.append(buffer.strip(" ").center(len_border))
            # center the text in the block after removing spaces
            buffer = ""

        content = "\n".join(lines)

        if ctx.guild:
            # using monospaced font to fix spacing
            await echo(ctx, member=ctx.author,
                       content=f"**```{BORDER_TOP}\n{ACCENT_BORDER}\n{content}\n{ACCENT_BORDER}\n{BORDER_BOTTOM}```**",
                       delete_msg=True)
        else:
            await ctx.send(f"**```{BORDER_TOP}\n{ACCENT_BORDER}\n{content}\n{ACCENT_BORDER}\n{BORDER_BOTTOM}```**")

    @commands.command()
    @commands.guild_only()
    async def poll(self, ctx: commands.Context,
                   prompt: str, timeout: typing.Optional[int] = 60, *options):
        '''
        Creates a poll, with an optional timeout.
        Specify a prompt, and then split options by spaces.

        ex. `$c poll "apples or bananas?" "apples are better" "bananas are the best!"`

        Polls automatically time out after 60 minutes by default.
        '''

        if len(options) < 36:

            lines = "\n".join(
                [f"{i+1}) {options[i]}" for i in range(len(options))])

            e = discord.Embed(
                title=f"**__POLL__:\n{prompt}**")

            for i in range(len(options)):
                e.add_field(color=0xd7342a,
                    name=f"{i+1}) {options[i]}: 0",
                    value="No one",
                    inline=False)
            e.set_author(
                name=f"{ctx.author.display_name}, react to this post with 🛑 to stop the poll.",
                icon_url=ctx.author.avatar_url)
            e.set_footer(
                text=f"Updated {local_time().strftime('%I:%M:%S %p %Z')}")

            msg = await ctx.send(embed=e)

            reacts = "123456789abcdefghijklmnopqrstuvwxyz"

            cont = True

            # Apply reactions
            for i in range(len(options)):
                await msg.add_reaction(textToEmoji(reacts[i]))
            await msg.add_reaction("🛑")

            def check(reaction, user):
                return reaction.message.id == msg.id and not user.bot

            while cont:
                # Await Responses
                try:
                    pending_tasks = [
                        self.bot.wait_for(
                            'reaction_add',
                            check=check,
                            timeout=60 * timeout),
                        self.bot.wait_for(
                            'reaction_remove',
                            check=check,
                            timeout=60 * timeout)]
                    done_tasks, pending_tasks = await asyncio.wait(pending_tasks, return_when=asyncio.FIRST_COMPLETED)

                    for task in pending_tasks:
                        task.cancel()

                    for task in done_tasks:
                        reaction, user = await task

                    if reaction.emoji == "🛑" and user == ctx.author:
                        raise asyncio.TimeoutError

                    e = discord.Embed(color=0xd7342a,
                        title=f"**__POLL__:\n{prompt}**")

                    for i in range(len(options)):

                        reaction = reaction.message.reactions[i]

                        users = [u.mention for u in await reaction.users().flatten() if u != self.bot.user]

                        people = " ".join(users)

                        e.add_field(
                            name=f"{i+1}) {options[i]}: {len(users)}",
                            value=people if people else "No one",
                            inline=False)
                    e.set_author(
                        name=f"{ctx.author.display_name}, react to this post with 🛑 to stop the poll.",
                        icon_url=ctx.author.avatar_url)
                    e.set_footer(
                        text=f"Updated {local_time().strftime('%I:%M:%S %p %Z')}")

                    await msg.edit(embed=e)

                except asyncio.TimeoutError:
                    cont = False

                    e = discord.Embed(color=0xd7342a,
                        title=f"**__POLL (Closed)__:\n{prompt}**")

                    for i in range(len(options)):

                        reaction = (await ctx.channel.fetch_message(msg.id)).reactions[i]

                        users = [u.mention for u in await reaction.users().flatten() if u != self.bot.user]

                        people = " ".join(users)

                        e.add_field(
                            name=f"{i+1}) {options[i]}: {len(users)}",
                            value=people if people else "No one",
                            inline=False)

                    e.set_author(name=f"Poll by {ctx.author.display_name}",
                                 icon_url=ctx.author.avatar_url)
                    e.set_footer(
                        text=f"Closed {local_time().strftime('%I:%M:%S %p %Z')}")

                    await msg.delete()
                    await ctx.send(embed=e)

        else:
            await ctx.send("Sorry, you can only choose up to 35 options at a time.")

    @commands.command()
    @commands.guild_only()
    async def createChannel(self, ctx: commands.Context, *, channelname: str):
        '''
        Creates a channel, and gives the user who
        created it full permissions over it.

        If "custom-channel-group" is set in the
        server cfg, it will create the channel there,
        otherwise it will be the same category as where
        the command was called.
        '''
        await ctx.trigger_typing()

        server_cfg: dict = collection("servers").find_one(ctx.guild.id)

        try:
            custom_group = server_cfg["channels"]["custom"]
        except Exception:
            if ctx.channel.category:
                custom_group = ctx.channel.category.id
            else:
                custom_group = 0

        if custom_group:
            # put in specific category
            group = ctx.guild.get_channel(custom_group)
            chn = await group.create_text_channel(channelname)
        else:
            # put in outside
            chn = await ctx.guild.create_text_channel(channelname)

        await chn.set_permissions(
            ctx.author, manage_channels=True, manage_roles=True)
        await ctx.send(f"Channel has been created at {chn.mention}")
