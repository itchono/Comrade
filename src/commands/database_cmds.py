from utils.utilities import *
from utils.mongo_interface import *
from utils.database_utils import *
import ast, os, dotenv
from pymongo import MongoClient

class Databases(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.THREAT_CACHE = {}
        self.OP_CACHE = {}

        dotenv.load_dotenv()
        self.client = MongoClient(os.environ.get('MONGOKEY'))
        self.DB = self.client[self.client.list_database_names()[0]]
        print(f"MongoDB Atlas Connected to Database: {self.client.list_database_names()[0]}")

        self._last_member = None

    async def on_load(self):
        '''
        Builds new users and servers on startup
        '''
        for g in self.bot.guilds:
            if not DBfind_one(SERVERCFG_COLLECTION, {"_id":g.id}): 
                DBupdate(SERVERCFG_COLLECTION, {"_id":g.id}, self.setupcfg(g.id))
                print(f"\t\tNew guild loaded: {g}")

            for m in g.members:
                if not DBfind_one(USERDATA_COLLECTION, {"server":g.id, "user":m.id}): 
                    DBupdate(USERDATA_COLLECTION, {"server":g.id, "user":m.id}, self.setupuser(m))
                    print(f"\t\tNew member loaded: {m}")
        print("Databases Ready")
    
    def setupuser(self, user: discord.Member):
        '''
        Configures a new user for use, returns a dictionary ready to be updated
        '''
        try: daily = DBcfgitem(user.guild.id,"default-daily-count")
        except: daily = 0

        return {
            "user": user.id,
            "name": user.name,
            "nickname": user.nick if user.nick else user.name,
            "threat-level": 0,
            "banned-words": [],
            "kick-votes": [],
            "mute-votes": [],
            "server": user.guild.id,
            "muted":False,
            "OP":False,
            "stop-pings": False,
            "stop-images": False,
            "daily-weight": daily if not user.bot else 0,
            "bot": user.bot,
            "last-online": "Now" if str(user.status) == "online" else "Never",
            "highest-guess-streak": 0,
            "check-when-online": []
            }

    def setupcfg(self, guild: discord.Guild):
        '''
        Configures a new server for use, returns a dictionary ready to be updated
        '''
        # attempt to locate channels
        log_channel = discord.utils.find(lambda c: "log" in c.name, guild.text_channels)
        emote_directory = discord.utils.find(lambda c: "emote" in c.name, guild.text_channels)

        return {
            "_id": guild.id,
            "joke-mode": True, # allows for joke stuff to happen
            "kick-requirement": 6,
            "mute-requirement": 4,
            "lethality-override": 0, # TODO defunct
            "zahando-threshold": 3,
            "banned-words": [],
            "announcements-channel": 0,
            "meme-channel": 0,
            "bot-channel": 0, # TODO defunct
            "log-channel": log_channel.id if log_channel else 0, # attempts to locate a log channel in the server
            "emote-directory": emote_directory.id if emote_directory else 0, # attempts to locate an emote directory in the server
            "custom-channel-group": 0, # id of the channel category under which you want to make custom channels
            "default-daily-count": 2, # amount of daily member counts everyone starts with
            "theme-colour": (215, 52, 42), # main colour for server; used in embeds
            "daily-member-colour": (241, 196, 15), # colour for daily member (RGB),
            "daily-member-staleness": 15, # enforces recency for daily members, in days. Set to -1 (or less) to disable.
            "za-hando-vote-duration": 120, # time to vote for ZA HANDO, in seconds
            "vault-vote-duration": 180 # time to vote for Vault post, in seconds
            }
    
    @commands.command()
    @commands.guild_only()
    @commands.check(isNotThreat())
    async def createChannel(self, ctx: commands.Context, *, channelname: str):
        '''
        Creates a channel, and gives the user who created it full permissions over it.

        If "custom-channel-group" is set in the server cfg, it will create the channel there, 
        otherwise it will be the same category as where the command was called.
        '''
        async with ctx.channel.typing():
            c = DBfind_one(SERVERCFG_COLLECTION, {"_id":ctx.guild.id})
            try: v = c["custom-channel-group"]
            except: 
                if k:= ctx.channel.category: v = k.id
                else: v = 0

            if v:
                # put in specific category
                group = ctx.guild.get_channel(v)
                chn = await group.create_text_channel(channelname)
            else: chn = await ctx.guild.create_text_channel(channelname) # put in outside

            await chn.set_permissions(ctx.author, manage_channels=True, manage_roles=True)
        await ctx.send(f"Channel has been created at {chn.mention}")

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def resetusers(self, ctx: commands.Context):
        '''
        POTENTIALLY DESTRUCTIVE. repopulates the UserData collection on Atlas with default values.
        '''
        for user in ctx.guild.members: updateDBuser(self.setupuser(user))
        await reactOK(ctx)

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def resetcfg(self, ctx: commands.Context):
        '''
        POTENTIALLY DESTRUCTIVE. Resets the configuration file for a server back to a default state. 
        '''
        DBupdate(USERDATA_COLLECTION, {"_id":ctx.guild.id}, self.setupcfg(ctx.guild))
        await reactOK(ctx)

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def updatealluserfields(self, ctx: commands.Context, fieldname, value):
        '''
        updates all fields of users to some given value.
        '''
        async with ctx.channel.typing():
            for user in ctx.guild.members:
                # each user is stored, themselves each as a dictionary
                d = DBuser(user.id, ctx.guild.id)
                try: d[fieldname] = ast.literal_eval(value)
                except: d[fieldname] = value
                updateDBuser(d)

        await reactOK(ctx)
        await ctx.send(f"All fields {fieldname} updated with value {value}")

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def user(self, ctx: commands.Context, tgt, DBcfgitem, value=None):
        '''
        Configures a user, mentioned by ping, id, or nickname. Leave value as none to delete field.
        '''
        u = DBuser((await extractUser(ctx, tgt)).id, ctx.guild.id)

        if not value:
            try:
                del u[DBcfgitem]
                updateDBuser(u)
                await delSend(ctx, "User config value deleted.")
            except: await delSend(ctx, "Value was not found.")
        else:
            try: u[DBcfgitem] = ast.literal_eval(value)
            except: u[DBcfgitem] = value
        updateDBuser(u)
        await reactOK(ctx)

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def cfg(self, ctx: commands.Context, DBcfgitem, value=None):
        '''
        Modifies a value in Comrade's configuration. Leave value blank to delete the field.
        '''
        c = DBfind_one(SERVERCFG_COLLECTION, {"_id":ctx.guild.id})
        if not value:
            try:
                del c[DBcfgitem]
                updateDB(SERVERCFG_COLLECTION, {"_id":ctx.guild.id}, c)
                await delSend(ctx, "Config value deleted.")
            except: await delSend(ctx, "Value was not found.")

        else:
            try: c[DBcfgitem] = ast.literal_eval(value)
            except: c[DBcfgitem] = value
            updateDB(SERVERCFG_COLLECTION, {"_id":ctx.guild.id}, c)

        await reactOK(ctx)

    @commands.command()
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context, full = None):
        '''
        Gets information about the server, with optional argument to view full configuration for server.
        '''
        s = ""

        if full:
            s = "Comrade Configuration:\n"
            c = DBfind_one(SERVERCFG_COLLECTION, {"_id":ctx.guild.id})
            for k in c:
                if k != "_id": s += str(k) + ": " + str(c[k]) + "\n"

        e = discord.Embed(title="Information for {}".format(
            ctx.guild.name), description=s, colour=discord.Colour.from_rgb(*DBcfgitem(ctx.guild.id,"theme-colour")))
        e.set_thumbnail(url=ctx.guild.icon_url)

        e.add_field(name="Server Created", value=ctx.guild.created_at.strftime('%B %m %Y at %I:%M:%S %p %Z'))
        e.add_field(name="Number of Text Channels", value=len(ctx.guild.text_channels))
        e.add_field(name="Number of Total Members", value=ctx.guild.member_count)
        e.add_field(name="Number of Human Members", value=len([i for i in ctx.guild.members if not i.bot]))
        e.add_field(name="Owner", value=ctx.guild.owner.mention)
        await ctx.send(embed=e)
        
    

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def injectEmotes(self, ctx: commands.Context):
        '''
        Inserts each image located inside the a folder called emotes and uploads it to the custom emotes channel in the server.
        
        Also useful for rebuilding the emote cache on command
        '''
        async with ctx.channel.typing():
            try:
                for n in os.listdir("emotes"):
                    with open("emotes/{}".format(n), "rb") as f:
                        msg = await ctx.send(file=discord.File(f))
                        url = msg.attachments[0].url
                        c = await getChannel(ctx.guild, "emote-directory")
                        await c.send(n[:n.index(".")] + "\n" + url)
            except:
                await ctx.send("Emotes could not be found on the host computer.")
            
            em = self.bot.get_cog("Emotes")
            await m.rebuildcache()
