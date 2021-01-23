# Macros
import discord
from discord.ext import commands

import re
import asyncio
import async_timeout
from discord.ext.commands.view import StringView

from db import collection
from utils.reactions import reactOK
from utils.users import random_member_from_server
from utils.checks import isNotThreat
from utils.utilities import is_url, bot_prefix
from config import cfg
from client import client as bot


MACRO_TIMEOUT = int(cfg["Performance"]["macro-timeout"])


async def process_macro(message: discord.message):
    '''
    Processes macro for a single message
    '''
    if message.author.bot or not message.content:
        return

    macros = collection("macros")

    # First, try fast loop for simple macros
    cmds = macros.find_one(
        {"server": message.guild.id, "name": message.content})
    args = []

    if not cmds:
        # Parse message into name and arguments
        args = message.content.split()
        name = args.pop(0)

        cmds = macros.find_one({"server": message.guild.id, "name": name})

        # Not found
        if not cmds:
            return 1

    cmds: str = cmds["macro"]

    if args:
        for arg in re.findall(r"\%([0-9])", cmds):
            try:
                cmds = cmds.replace(f"%{arg}", args[int(arg)-1])
            # Too few arguments
            except IndexError:
                await message.channel.send(
                    f"Too few arguments for macro {name}")
                return 3

    async with async_timeout.timeout(MACRO_TIMEOUT):
        try:
            print_queue = []
            # I need this, so that I can print multiline messages

            # nonempty lines in the macro
            for line in filter(lambda l: l,
                               map(lambda l: l.strip(), cmds.splitlines())):

                if line.split()[0].lower() == "wait":
                    await asyncio.sleep(float(line.split()[1]))
                else:
                    # Trick discord.py into parsing this command as a bot
                    view = StringView(line)
                    ctx = commands.Context(
                        prefix=bot_prefix, view=view, bot=bot, message=message)
                    invoker = view.get_word()
                    ctx.invoked_with = invoker

                    if command := bot.all_commands.get(invoker):
                        if print_queue:
                            # We have run into a command, send ze messages
                            await ctx.send("\n".join(print_queue))
                            print_queue.clear()

                        # invoke a command
                        ctx.command = command
                        await bot.invoke(ctx)
                    else:
                        # Push string to queue
                        print_queue.append(line.lstrip("\\"))

            if print_queue:
                # We have run to the end, send ze messages
                await message.channel.send("\n".join(print_queue))

        except (asyncio.CancelledError, asyncio.TimeoutError):
            await message.channel.send(
                f"Command execution timed out after {MACRO_TIMEOUT} seconds.")
            return 2
    return 0


class Macros(commands.Cog):
    '''
    Set the bot to say something whenever you type a certain
    message in chat.

    Can write more advanced macros to execute scripts
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if not message.author.bot and message.guild:
            await process_macro(message)

            # Fun features
            if "@someone" in message.content.lower():
                e = discord.Embed(
                    description=random_member_from_server(message.guild.id, True).mention)
                e.set_footer(
                    text=f"Random ping by: {message.author.display_name}")
                await message.channel.send(embed=e)

            if not isNotThreat(2)(
                await self.bot.get_context(message)) and (len(
                    message.attachments) + len(
                    message.embeds) > 0 or is_url(message.content)):

                e = discord.Embed(title="You just posted cringe")
                e.set_image(
                    url=
                    "https://cdn.discordapp.com/attachments/419214713755402262/709165272447057981/unknown-11.png"
                )
                await message.channel.send(embed=e)
            # TODO: Re-add meme review in some capacity

    @commands.command()
    @commands.guild_only()
    async def macro(self, ctx: commands.Context, name: str, *args):
        '''
        Runs a macro, with arguments
        '''
        if ctx.invoked_subcommand is None:
            result = await process_macro(ctx.message)
            if result == 1:
                await ctx.send(f"Macro `{name}` not found.")

    @commands.command(aliases=["addtrigger"])
    @commands.guild_only()
    async def addmacro(self, ctx: commands.Context, name: str, *, macro):
        '''
        Adds a macro; a sequence of commands and text callable when a user types a message.
        At the most basic level, you can input text, which will be said when it's called.
        You can also call commands by specifying the command name.

        Special Things:
            Use `\` to escape calling commands.
            Use `wait` to delay execution of a function by number of seconds.
            Pass in variables using %1, %2, %3...

        Example: a macro called tomato

        ascii 🍅 b
        wait 5
        $1 is the best game
        \defaultdance
        anime
        defaultdance

        call it using `tomato minecraft`

        output:
        🍅🍅
        🍅  🍅
        🍅🍅
        🍅  🍅
        🍅🍅
        minecraft is the best game
        defaultdance
        anime
        ⠀⠀⠀⠀⣀⣤
        ⠀⠀⠀⠀⣿⠿⣶
        ⠀⠀⠀⠀⣿⣿⣀
        ⠀⠀⠀⣶⣶⣿⠿⠛⣶
        ⠤⣀⠛⣿⣿⣿⣿⣿⣿⣭⣿⣤
        ⠒⠀⠀⠀⠉⣿⣿⣿⣿⠀⠀⠉⣀
        ⠀⠤⣤⣤⣀⣿⣿⣿⣿⣀⠀⠀⣿
        ⠀⠀⠛⣿⣿⣿⣿⣿⣿⣿⣭⣶⠉
        ⠀⠀⠀⠤⣿⣿⣿⣿⣿⣿⣿
        ⠀⠀⠀⣭⣿⣿⣿⠀⣿⣿⣿
        ⠀⠀⠀⣉⣿⣿⠿⠀⠿⣿⣿
        ⠀⠀⠀⠀⣿⣿⠀⠀⠀⣿⣿⣤
        ⠀⠀⠀⣀⣿⣿⠀⠀⠀⣿⣿⣿
        ⠀⠀⠀⣿⣿⣿⠀⠀⠀⣿⣿⣿
        ⠀⠀⠀⣿⣿⠛⠀⠀⠀⠉⣿⣿
        ⠀⠀⠀⠉⣿⠀⠀⠀⠀⠀⠛⣿
        ⠀⠀⠀⠀⣿⠀⠀⠀⠀⠀⠀⣿⣿
        ⠀⠀⠀⠀⣛⠀⠀⠀⠀⠀⠀⠛⠿⠿⠿
        ⠀⠀⠀⠛⠛

        TIP: use shift+enter to make new lines
        TIP: OR use \`\`\` \`\`\` on Discord to help format your command
        '''
        cmds = collection(
            "macros").find_one({"server": ctx.guild.id, "name": name})

        if cmds:
            await ctx.send(f"Macro with name `{name}` already exists!")
            return

        collection(
            "macros").insert_one(
                {"server": ctx.guild.id,
                 "name": name,
                 "macro": macro.strip("```").strip("\n")}
                )
        await reactOK(ctx)

    @commands.command(aliases=["listmacros", "macrolist", "macros"])
    @commands.guild_only()
    async def listmacro(self, ctx: commands.context):
        '''
        Lists all macros in the server
        '''
        macros = collection(
            "macros").find({"server": ctx.guild.id})
        if macros:
            e = discord.Embed(
                title=f"Macros for {ctx.guild.name}",
                description="\n".join(i["name"] for i in macros))
            await ctx.send(embed=e)
        else:
            await ctx.send(f"No macros found in {ctx.guild.name}")

    @commands.command()
    @commands.guild_only()
    async def removemacro(self, ctx: commands.Context, name):
        '''
        Deletes a macro
        '''
        collection("macros").delete_one(
            {"server": ctx.guild.id, "name": name})
        await reactOK(ctx)

    @commands.command()
    @commands.guild_only()
    async def showmacro(self, ctx: commands.Context, name):
        '''
        Show the script content of a macro
        '''
        cmds = collection(
            "macros").find_one({"server": ctx.guild.id, "name": name})
        if not cmds:
            await ctx.send("Macro not found.")
            return
        await ctx.send(
            f"```{cmds['macro']}```")
