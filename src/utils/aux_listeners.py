from utils.utilities import *
from utils.mongo_interface import *

import datetime

class AuxilliaryListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, user:discord.Member):
        '''
        When a member joins the server.
        '''
        # member join
        print("Join {}".format(user.name))
        d = {"user":user.id}
        d["name"] = user.name
        d["nickname"] = user.nick if user.nick else user.name
        d["threat level"] = 0
        d["banned words"] = []
        d["kick votes"] = []
        d["server"] = user.guild.id
        d["OP"] = False
        d["daily weight"] = 0

        updateUser(d)

    @commands.Cog.listener()
    async def on_member_update(self, before, user):
        '''
        Whenever a server member changes their state.
        '''
        if (user.display_name != before.display_name):
            # member update
            print("Updated {}".format(user.name))
            d = getUser(before.id, user.guild.id)
            d["name"] = user.name
            d["nickname"] = user.nick if user.nick else user.name

            updateUser(d)

        elif user.status != before.status:
            # status update
            e = discord.Embed(title = "Status Change: {}".format(user.display_name), 
                                description = "Time: {}\n{} --> {}". format(datetime.datetime.now().strftime("%H:%M:%S"),before.status, user.status),
                                colour = discord.Color.from_rgb(51, 204, 51))
            await log(user.guild, "",e)

    @commands.Cog.listener()
    async def on_user_update(self, before, user):
        '''
        Whenever a general user changes their state.
        '''
        if (user.name != before.name):
            # user update
            print("Updated {}".format(user.name))

            POSSIBLES = userQuery({"user":user.id})
            for u in POSSIBLES:
                u["name"] = user.name
                updateUser(u)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction:discord.Reaction, user:discord.User):
        '''
        When a user adds a reaction to a message.
        '''
        # self-cleanup
        if reaction.message.author == self.bot.user and reaction.emoji == "🗑️" and user != self.bot.user:
            await reaction.message.delete()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, exception):
        '''
        When a command fails to execute
        '''
        await reactQuestion(ctx)
        await log(ctx.guild, "Failure: {}\nType: {}".format(exception, type(exception)))
        if type(exception) == commands.CheckFailure:
            await timedSend("You have insufficient permission to use this command {}".format(ctx.author.mention), ctx.channel)

        elif type(exception) == commands.CommandNotFound:
            await timedSend("'{}' is not a valid command.".format(ctx.message.content), ctx.channel)
        else:
            await timedSend("Failure: {}".format(exception), ctx.channel)

        
    

