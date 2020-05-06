from utils.utilities import *
from utils.mongo_interface import *

class AuxilliaryListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, user:discord.Member):
        # member join
        print("Join {}".format(user.name))
        d = {"_id":user.id}
        d["name"] = user.name
        d["nickname"] = user.nick if user.nick else user.name
        d["threat level"] = 0
        d["banned words"] = []
        d["kick votes"] = []
        d["Bot"] = user.bot
        d["OP"] = False
        d["daily count"] = 0

        updateUser(d)

    @commands.Cog.listener()
    async def on_member_update(self, before, user):
        if (user.display_name != before.display_name):
            # member update
            print("Updated {}".format(user.name))
            d = getUser(before.id)
            d["name"] = user.name
            d["nickname"] = user.nick if user.nick else user.name

            updateUser(d)
        elif user.status != before.status:
            ch = user.guild.get_channel(int(getCFG(user.guild.id)["log channel"]))
            e = discord.Embed(title = "Status Change: {}".format(user.display_name), 
                                description = "{} --> {}". format(before.status, user.status),
                                colour = discord.Color.from_rgb(51, 204, 51))
            await ch.send(embed=e)

    @commands.Cog.listener()
    async def on_user_update(self, before, user):
        if (user.name != before.name):
            # user update
            print("Updated {}".format(user.name))
            d = getUser(before.id)
            d["name"] = user.name
            d["nickname"] = user.nick if user.nick else user.name

            updateUser(d)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:discord.Reaction, user:discord.User):
    
        # self-cleanup
        if reaction.message.author == self.bot.user and reaction.emoji == "🗑️" and user != self.bot.user:
            await reaction.message.delete()
