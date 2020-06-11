from utils.utilities import *
from utils.mongo_interface import *

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def version(self, ctx:commands.Context):
        '''
        Logs version of the bot.
        '''
        await ctx.send("Comrade is running version: 3.0 alpha build June 11 v2")

    @commands.command()
    async def host(self, ctx: commands.Context):
        '''
        Returns name of host machine.
        '''
        await ctx.send("Comrade is currently hosted from: {}. Local time: {}".format(getHost(), localTime().strftime("%I:%M:%S %p %Z")))

    @commands.command()
    async def clearcommands(self, ctx:commands.Context):
        '''
        Cleans up commands from sent from users in a channel.
        '''
        await ctx.channel.purge(check=isCommand, bulk=True)

    @commands.command()
    @commands.check(isOwner)
    async def shutdown(self, ctx:commands.Context):
        '''
        Logs out the user.
        '''
        await self.bot.logout()

    @commands.command()
    @commands.check(isnotThreat)
    async def dmUser(self, ctx: commands.Context, target, message:str):
        '''
        DM given user
        Made by vdoubleu
        '''
        await ctx.trigger_typing()
        
        if u := await extractUser(ctx, target):

            e = discord.Embed(title="", description = "Sent by {}".format(ctx.author))
            
            await DM(message, u, e)
            await reactOK(ctx)
            await ctx.send("DM sent to {}".format(target), delete_after=10)

    @commands.command()
    async def msgInfo(self, ctx: commands.Context, msgid):
        '''
        Gets information about a specific message given an ID.
        '''
        msg = await ctx.channel.fetch_message(msgid)
        await ctx.send("Author: {}".format(msg.author))

    @commands.command()
    async def cmdtest(self, ctx):
        m = await ctx.send("$c help")
        await self.bot.invoke()

    @commands.command(name = "list")
    async def customlist(self, ctx, operation, title=None, value=None):
        '''
        Displays a lists, or adds
        '''
        if operation in {"make", "add", "remove", "show", "all"}:

            if operation == "make":
                l = []
                updatecustomList(ctx.guild.id, title, l)
                await reactOK(ctx)

            elif operation == "show":
                l = getcustomList(ctx.guild.id, title)
                if l is not None:
                    await ctx.send("{}:\n{}".format(title, l))
                else:
                    await delSend("List not found.", ctx.channel)
            elif operation == "add":
                l = getcustomList(ctx.guild.id, title)
                if l is not None:
                    l.append(value)
                    updatecustomList(ctx.guild.id, title, l)
                    await reactOK(ctx)
                else:
                    await delSend("List not found.", ctx.channel)

            elif operation == "remove":
                l = getcustomList(ctx.guild.id, title)
                if l is not None:
                    try:
                        l.remove(value)
                        updatecustomList(ctx.guild.id, title, l)
                        await reactOK(ctx)
                    except:
                        await delSend("Element {} not found.".format(value), ctx.channel)
                else:
                    await delSend("List not found.", ctx.channel)

            elif operation == "all":
                await ctx.send("{}".format([i["name"] for i in listcustomLists(ctx.guild.id)]))



    

