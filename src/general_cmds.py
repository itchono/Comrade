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
        await ctx.send("Comrade is running version: 3.0alpha build May 17")

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
        
        if u := await extractUser(self.bot, ctx, target):

            e = discord.Embed(title="", description = "Sent by {}".format(ctx.author))
            
            await DM(message, u, e)
            await reactOK(ctx)
            await timedSend("DM sent to {}".format(target), ctx.channel)

    @commands.command()
    async def msgInfo(self, ctx, msgid):
        '''
        Gets information about a specific message given an ID.
        '''
        msg = await ctx.channel.fetch_message(msgid)
        await ctx.send("Author: {}".format(msg.author))

    

    

