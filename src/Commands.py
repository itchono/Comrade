from Utilities import *

from MongoInterface import *

class Commands(commands.Cog):
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
    async def getuser(self, ctx, nickname):
        '''
        Looks up a user based on their server nickname, returning a dictionary with the document entry
        HINT: Use Quotes like this "A user's name" to deal with names containing spaces
        '''
        await delSend("{}".format(getUserfromNick(nickname)), ctx.channel)

    @commands.command()
    async def buymefood(self, ctx:commands.Context):
        await delSend("Enter Your Credit Card Info...", ctx.channel)

    @commands.command()
    @commands.check(isOwner)
    async def cfg(self, ctx:commands.Context, cfgitem, value):
        '''
        modifies a value in Comrade's configuration.
        '''
        c = getCFG(ctx.guild.id)

        try:
            c[cfgitem] = eval(str(value))
        except:
            c[cfgitem] = value
        updateCFG(c)

        await delSend("Value updated.", ctx.channel)

    @commands.command()
    async def cfgstatus(self, ctx:commands.Context):
        c = getCFG(ctx.guild.id)

        s = ""

        for k in c:
            if k != "_id":
                s += str(k) + ": " + str(c[k]) + "\n"
        
        e = discord.Embed(
            title="Comrade Configuration for {}".format(ctx.guild.name),
            description = s,
            colour = discord.Colour.from_rgb(r=215, g=52, b=42)
            )

        await ctx.send(embed=e)


    @commands.command()
    @commands.check(isOwner)
    async def reloadusers(self, ctx:commands.Context):
        '''
        repopulates the UserData collection on Atlas with default values
        '''
        for user in ctx.guild.members:
            # each user is stored, themselves each as a dictionary

            d = {"_id":user.id}
            d["name"] = user.name
            d["nickname"] = user.nick if user.nick else user.name
            d["threat level"] = 0
            d["banned words"] = []
            d["kick votes"] = []
            d["OP"] = False

            updateUser(d)

        await delSend("Update Complete", ctx.channel)
    
    