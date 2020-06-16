from utils.utilities import *
from utils.mongo_interface import *

import datetime
import traceback
import sys

class AuxilliaryListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_member_join(self, user: discord.Member):
        '''
        When a member joins the server.
        '''
        # member join
        await log(user.guild, "Join {}".format(user.name))
        
        stp = self.bot.get_cog("Setup")

        updateUser(stp.setupuser(user))

        cog = self.bot.get_cog("Users")
        await cog.rebuildUserCache(user.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, user: discord.Member):
        '''
        When a member leaves the server
        TODO reconfigure user DB
        '''
        await log(user.guild, "Left {}".format(user.name))
        c = self.bot.get_channel(getCFG(user.guild.id)["announcements channel"])
        await c.send(f":door: {user.display_name} has left.")

    @commands.Cog.listener()
    async def on_member_update(self, before, user):
        '''
        Whenever a server member changes their state.
        '''
        if (user.display_name != before.display_name):
            # member update
            d = getUser(before.id, user.guild.id)
            d["name"] = user.name
            d["nickname"] = user.nick if user.nick else user.name
            updateUser(d)
            await log(user.guild, "Member Updated: {}".format(before.name))

        elif user.status != before.status:
            # status update

            if str(user.status) == "offline":
                d = getUser(before.id, user.guild.id)
                d["last online"] = localTime().strftime("%I:%M:%S %p %Z")
                updateUser(d)
            else:
                d = getUser(before.id, user.guild.id)
                d["last online"] = "now"
                updateUser(d)

    @commands.Cog.listener()
    async def on_user_update(self, before, user):
        '''
        Whenever a general user changes their state.
        '''
        if (user.name != before.name):
            # user update
            POSSIBLES = userQuery({"user":user.id})
            for u in POSSIBLES:
                u["name"] = user.name
                updateUser(u)

            await log(user.guild, "User Updated: {}".format(before.name))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction,
                              user: discord.User):
        '''
        When a user adds a reaction to a message.
        '''
        # self-cleanup
        if reaction.message.author == self.bot.user and reaction.emoji == "🗑️" and user != self.bot.user:
            await reaction.message.delete()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, exception):
        # When a command fails to execute
        if not (type(exception) == commands.CheckFailure or type(exception) == commands.CommandNotFound):
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
        
        if ctx.guild: await log(ctx.guild, "Failure: {}\nType: {}\nTraceback:{}".format(exception, type(exception), exception.__traceback__))
        else: await ctx.send("```Failure: {}\nType: {}\nTraceback:{}```".format(exception, type(exception), exception.__traceback__))

        if type(exception) == commands.NoPrivateMessage:
            await reactX(ctx)
            await delSend(ctx, "This command can only be used in a server.")
            
        elif type(exception) == commands.CheckFailure:
            await reactX(ctx)
            await ctx.send("You have insufficient permission to use this command {}".
                format(ctx.author.mention), delete_after=10)
        
        elif type(exception) == commands.NSFWChannelRequired:
            await reactX(ctx)
            await delSend(ctx, "This command can only be used in a NSFW channel.")
            
        elif type(exception) == commands.CommandNotFound:
            await reactQuestion(ctx)
            await ctx.send("'{}' is not a valid command.".format(ctx.message.content), delete_after=10)

        else:
            await reactQuestion(ctx)
            await ctx.send("Failure: {}".format(exception), delete_after=10)

        
