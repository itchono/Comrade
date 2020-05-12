from utils.utilities import *
from utils.mongo_interface import *

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def clearcommands(self, ctx:commands.Context):
        '''
        Cleans up commands from sent from users in a channel.
        '''
        await ctx.channel.purge(check=isCommand, bulk=True)

    @commands.command()
    async def buymefood(self, ctx: commands.Context):
        '''
        Maybe buys you food
        '''
        await delSend("Enter Your Credit Card Info...", ctx.channel)

    @commands.command()
    @commands.check(isnotThreat)
    async def dmUser(self, ctx: commands.Context, target, message:str):
        '''
        DM given user
        Made by vdoubleu
        '''
        await ctx.trigger_typing()
        
        if u := await extractUser(self.bot, ctx, target):
            
            await DM(message, u)

            await reactOK(ctx)

    @commands.command()
    async def msgInfo(self, ctx, msgid):
        '''
        Gets information about a specific message given an ID.
        '''
        msg = await ctx.channel.fetch_message(msgid)
        await ctx.send("Author: {}".format(msg.author))

    

