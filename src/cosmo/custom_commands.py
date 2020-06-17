from utils.utilities import *
from utils.mongo_interface import *

from cosmo.cosmo_interp import *
from cosmo.cosmo_parser import *

from discord.ext.commands.view import StringView

class Cosmo(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.check(isnotThreat)
    async def macro(self, ctx, *, cmds):
        '''
        Macro runner for Comrade.

        Split command queries by comma. 
        SPECIAL COMMANDS:
        use "wait" to delay execution of a function by a set time
        use "say" to send a message with some content

        ex. <prefix> macro help, wait 5, version, dmuser itchono hello sir
        '''
        for i in cmds.split(","):
            i = i.strip(" ")
            try:
                if i.split(" ")[0].lower() == "wait":
                    await asyncio.sleep(float(i.split(" ")[1]))

                elif i.split(" ")[0].lower() == "say":
                    await asyncio.wait_for(ctx.send(" ".join(i.split(" ")[1:])), timeout=5.0)
                else:
                    try:
                        i = BOT_PREFIX + i
                        view = StringView(i)
                        ctx2 = commands.Context(prefix=BOT_PREFIX, view=view, bot=self.bot, message=ctx.message)
                        view.skip_string(BOT_PREFIX)

                        invoker = view.get_word()
                        ctx2.invoked_with = invoker
                        ctx2.command = self.bot.all_commands.get(invoker)

                        await asyncio.wait_for(self.bot.invoke(ctx2), timeout=5.0)
                        
                    except: await ctx.send(f"Input {i} could not be processed.")
            except: await ctx.send(f"Input {i} could not be processed.")

    @commands.command()
    @commands.guild_only()
    @commands.check(isnotThreat)
    async def showscripts(self, ctx):
        '''
        Lists all Cosmo scripts in the server
        '''
        e = discord.Embed(title=f"Scripts for {ctx.guild.name}", colour=discord.Colour.from_rgb(*THEME_COLOUR))

        scrs = allcmds(ctx.guild.id)

        e.add_field(name="Cosmo Scripts", value=", ".join([i["name"] for i in scrs if i["type"] == "cosmo"]), inline=True)
        e.add_field(name="Macros", value=", ".join([i["name"] for i in scrs if i["type"] == "macro"]), inline=True)
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    @commands.check(isOP)
    async def removescript(self, ctx, name):
        '''
        Deletes a Cosmo script
        '''
        removeCmd(ctx.guild.id, name)
        await reactOK(ctx)


    @commands.command()
    @commands.guild_only()
    @commands.check(isnotThreat)
    async def showscript(self, ctx, name):
        '''
        Shows a Cosmos script
        '''
        if tup := getCmd(ctx.guild.id, name):

            (cmd, cmdType) = tup
            if cmdType == "cosmo":
                await ctx.send(f"```{cmd}```") 
            else:
                # macro
                await ctx.send(f"`{cmd}`")

        else:
            await reactX(ctx)
            await ctx.send(f"No script with name {name} was found.", delete_after=10)


    @commands.command()
    @commands.guild_only()
    @commands.check(isnotThreat)
    async def run(self, ctx, *, args):
        '''
        Runs a macro, or a stored Cosmo script, with a given name, and optional arguments [SPLIT BY COMMA].

        Built on Victor's Cosmo language and Comrade's macro system
        '''
        args = args.split(",")
        name = args.pop(0)

        if tup := getCmd(ctx.guild.id, name):

            (cmd, cmdType) = tup

            if cmdType == "cosmo":

                splt_line_lst = token_list(cmd)

                try:
                    if splt_line_lst[0][-1] == "]" and splt_line_lst[0][0] == "[":

                        params = [i.strip(" ") for i in splt_line_lst[0].strip("[").strip("]").split(",")]
                        # inject args

                        if len(args) == len(params):
                            splt_line_lst[0] = str([f'{params[i]}:{args[i]}' for i in range(len(args))]).replace("'","")
                        else:
                            await ctx.send(f"Not enough arguments for this script. Needs to be of form `{BOT_PREFIX}run {name} {splt_line_lst[0].strip('[').strip(']')}`")
                            return

                except:
                    pass

                #get env from first line
                env = get_env(splt_line_lst)
                #parse program
                ast = parse(splt_line_lst)
                #interp ast with given env

                try:
                    cmds = await asyncio.wait_for(interp(ast, env, extCall=True), timeout=INTERP_TIMEOUT)
                    await self.macro(ctx, cmds=",".join(cmds))

                except asyncio.TimeoutError:
                    await ctx.send(f"Program interpretation failed after {INTERP_TIMEOUT} seconds. Check to see if you have any infinite loops running!")
            else:
                try:
                    await asyncio.wait_for(self.macro(ctx, cmds=cmd), timeout=1.0)
                except asyncio.TimeoutError:
                    await ctx.send("Program execution terminated after 30 seconds.")

        else:
            await reactX(ctx)
            await ctx.send(f"No script with name {name} was found.", delete_after=10)

    @commands.command()
    @commands.guild_only()
    async def newscript(self, ctx, command_name, *, command):
        '''
        Creates a command using a Cosmo script or Comrade Macro

        INPUT FORMAT: <bot prefix> createcmd <command name> ```<CODE GOES HERE>```
        '''

        if command[:3] == "```" and command[-3:] == "```":
            updateCmd(ctx.guild.id, command_name, command.strip("```"), "cosmo")
        else:
            updateCmd(ctx.guild.id, command_name, command, "macro")
        await reactOK(ctx)


    