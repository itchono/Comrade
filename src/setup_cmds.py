from utils.utilities import *
from utils.mongo_interface import *


class Setup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    
    def setupuser(self, user: discord.Member):

        d = {"user": user.id}
        d["name"] = user.name
        d["nickname"] = user.nick if user.nick else user.name
        d["threat level"] = 0
        d["banned words"] = []
        d["kick votes"] = []
        d["server"] = user.guild.id
        d["OP"] = False
        d["daily weight"] = 2
        d["bot"] = user.bot

        return d

    @commands.command()
    @commands.check(isOwner)
    async def reloadusers(self, ctx: commands.Context):
        '''
        POTENTIALLY DESTRUCTIVE. repopulates the UserData collection on Atlas with default values.
        '''
        await ctx.channel.trigger_typing()
        for user in ctx.guild.members:
            # each user is stored, themselves each as a dictionary
            updateUser(self.setupuser(user))
        await reactOK(ctx)

    @commands.command()
    @commands.check(isOwner)
    async def updatealluserfields(self, ctx: commands.Context, fieldname,
                                  value):
        '''
        updates all fields of users to some given value.
        '''
        await ctx.channel.trigger_typing()

        for user in ctx.guild.members:
            # each user is stored, themselves each as a dictionary

            d = getUser(user.id, ctx.guild.id)

            try:
                d[fieldname] = eval(str(value))
            except:
                d[fieldname] = value

            updateUser(d)

        await reactOK(ctx)

    @commands.command()
    @commands.check(isOwner)
    async def user(self, ctx: commands.Context, tgt, cfgitem, value=None):
        '''
        Configures a user, mentioned by ping, id, or nickname. Leave value as none to delete field.
        '''
        u = getUser((await extractUser(ctx, tgt)).id, ctx.guild.id)

        if not value:
            try:
                del u[cfgitem]
                updateUser(u)
                await delSend("User config value deleted.", ctx.channel)
            except:
                await delSend("Value was not found.", ctx.channel)

        else:
            try:
                u[cfgitem] = eval(str(value))
            except:
                u[cfgitem] = value
            updateUser(u)

            await reactOK(ctx)

    @commands.command()
    @commands.check(isOwner)
    async def cfg(self, ctx: commands.Context, cfgitem, value=None):
        '''
        Modifies a value in Comrade's configuration. Leave value blank to delete the field.
        '''
        c = getCFG(ctx.guild.id)

        if not value:
            try:
                del c[cfgitem]
                updateCFG(c)
                await delSend("Config value deleted.", ctx.channel)
            except:
                await delSend("Value was not found.", ctx.channel)

        else:
            try:
                c[cfgitem] = eval(str(value))
            except:
                c[cfgitem] = value
            updateCFG(c)

            await reactOK(ctx)

    @commands.command()
    async def cfgstatus(self, ctx: commands.Context):
        '''
        Sends an embed providing a dump of all Comrade configuration data for this server.
        '''
        c = getCFG(ctx.guild.id)

        s = ""

        for k in c:
            if k != "_id":
                s += str(k) + ": " + str(c[k]) + "\n"

        e = discord.Embed(title="Comrade Configuration for {}".format(
            ctx.guild.name),
                          description=s,
                          colour=discord.Colour.from_rgb(r=215, g=52, b=42))
        e.set_thumbnail(url=ctx.guild.icon_url)

        await ctx.send(embed=e)

    @commands.command()
    @commands.check(isOwner)
    async def resetcfg(self, ctx: commands.Context):
        '''
        POTENTIALLY DESTRUCTIVE. Resets the configuration file for a server back to a default state. 
        '''
        d = {"_id": ctx.guild.id}
        d["last daily"] = "2020-05-04"  # default "time = 0" for comrade
        d["joke mode"] = True
        d["kick requirement"] = 6
        d["lethality override"] = 0
        d["zahando threshold"] = 3
        d["announcements channel"] = -1
        d["meme channel"] = -1
        d["bot channel"] = -1
        d["log channel"] = -1
        d["hentai channel"] = -1
        d["emote directory"] = -1
        updateCFG(d)

        await reactOK(ctx)

    @commands.command()
    @commands.check(isOwner)
    async def injectEmotes(self, ctx: commands.Context):
        '''
        Inserts each image located inside the a folder called emotes and uploads it to the custom emotes channel in the server.
        '''
        for n in os.listdir("emotes"):
            with open("emotes/{}".format(n), "rb") as f:
                msg = await ctx.send(file=discord.File(f))
                url = msg.attachments[0].url
                c = await getChannel(ctx.guild, "emote directory")
                await c.send(n[:n.index(".")] + "\n" + url)
