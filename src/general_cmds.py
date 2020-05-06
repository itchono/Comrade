from utils.utilities import *
from utils.mongo_interface import *

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def memeapproved(self, ctx:commands.Context):
        '''
        Approves a meme.
        '''
        await delSend("Meme approved", ctx.channel)

    @commands.command()
    async def getuser(self, ctx:commands.Context, nickname):
        '''
        Looks up a user based on their server nickname, returning a dictionary with the document entry
        HINT: Use Quotes like this "A user's name" to deal with names containing spaces
        '''
        await delSend("{}".format(getUserfromNick(nickname)), ctx.channel)

    @commands.command()
    async def echo(self, ctx:commands.Context, text:str):
        '''
        Echoes a command back to the user under their form
        '''
        
        member = ctx.guild.get_member(self.bot.user.id)

        old = member.display_name

        await member.edit(nick=ctx.author.display_name)

        await ctx.send(text)

        await member.edit(nick=old)

    @commands.command()
    async def buymefood(self, ctx:commands.Context):
        '''
        Maybe buys you food
        '''
        await delSend("Enter Your Credit Card Info...", ctx.channel)


    
    