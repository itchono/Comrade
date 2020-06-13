from utils.utilities import *
from utils.mongo_interface import *

from importlib import reload
import parser

class Crimson(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cmd = ""
        self._last_member = None

    async def execute_command(self, ctx : commands.Context, cmdText : str):
        '''
        Executes custom commnd in given context
        '''
        function = ("class CMDS(commands.Cog):\n")
        function += ("\tdef __init__(self, bot):\n\t\tself.bot = bot\n\t\tself._last_member = None\n")

        for l in cmdText.splitlines():
            function += ("\t{}\n".format(l))
        function += ("self.bot.add_cog(CMDS(self.bot))\n")
        
        exec(function)

        c = self.bot.get_cog('CMDS')
        try:
            await c.func(ctx)
        except:
            await ctx.send("Something went wrong parsing the command.")
        self.bot.remove_cog("CMDS")

    def command_builder(self, rawcmd : str):
        '''
        Constructs custom command based on stripped down Cosmo code.
        '''
        content = "@commands.command()\nasync def func(self, ctx):\n"

        callLookup = {"CALL":(lambda *args: "await self.bot.get_command('{}').__call__(ctx, {})".format(args[0], str(["{}".format(i) for i in args[1:]]).strip("]").strip("[")) if len(args) > 1 else "await self.bot.get_command('{}').__call__(ctx)".format(args[0])),
        "PRINT":(lambda *args: "await ctx.send('{}')".format(" ".join(args)))}

        for l in rawcmd.splitlines():
            tokens = l.split(" ")
            if len(tokens) < 2: tokens.append(None)
            try:
                content += "\t" + callLookup[tokens[0]](*tokens[1:]) + "\n"
            except:
                pass

        return content

    @commands.command()
    @commands.guild_only()
    async def runcmd(self, ctx, name):
        '''
        Runs a command.
        '''
        await self.execute_command(ctx, getCmd(ctx.guild.id, name))

    @commands.command()
    @commands.guild_only()
    async def createcmd(self, ctx, *, args):
        '''
        Creates a command using a simplified Cosmo script.
        '''
        name = args.split(" ")[0]
        cmdText = " ".join(args.split(" ")[1:])
        cmd = self.command_builder(cmdText.strip("```"))
        updateCmd(ctx.guild.id, name, cmd)
        await reactOK(ctx)


    