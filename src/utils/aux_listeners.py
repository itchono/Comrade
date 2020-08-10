from utils.utilities import *


import datetime
import traceback
import sys

class AuxilliaryListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.Cog.listener()
    async def on_member_join(self, user: discord.Member):
        '''
        When a member joins the server.
        '''
        # member join
        await log(user.guild, "Join {}".format(user.name))
        
        stp = self.bot.get_cog("Databases")

        updateDBuser(stp.setupuser(user))

        cog = self.bot.get_cog("Users")
        await cog.rebuildcache(user.guild)

    @commands.Cog.listener()
    async def on_member_remove(self, user: discord.Member):
        '''
        When a member leaves the server
        '''
        await log(user.guild, "Left {}".format(user.name))
        c = self.bot.get_channel(DBcfgitem(user.guild.id,"announcements-channel"))

        DBremove_one(USER_COL, {"server":user.guild.id, "user":user.id})
        await c.send(f":door: {user.display_name} has left.")

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        '''
        When a message edit is detected
        '''

        if message := payload.cached_message:

            if not message.author.bot and message.guild:
                await log(message.guild, f"Message edited by {message.author.display_name} ({message.author}) in {message.channel.mention} [link]({message.jump_url})\nOriginal Content: ```{message.content}```")

        elif not message.author.bot and message.guild:
            message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)
            await log(message.guild, f"Message edited by {message.author.display_name} ({message.author}) in {message.channel.mention} [link]({message.jump_url})")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        '''
        When a message is deleted
        '''
        if msg := payload.cached_message:
            if msg.guild and not msg.author.bot:
                await log(msg.guild, f"Message sent by {msg.author.display_name} ({msg.author}) deleted in {msg.channel.mention}\n Content: ```{msg.content}```")

                if msg.mentions: await msg.channel.send(f":rotating_light: PING POLICE :rotating_light:\n{msg.author.mention} deleted a message which pinged the following user(s): {', '.join(['`' + m.display_name + '`' for m in msg.mentions])}")

        elif payload.guild:
            await log(self.bot.get_guild(payload.guild_id), f"Message deleted in {(self.bot.get_channel(payload.channel_id))}")

    @commands.Cog.listener()
    async def on_member_update(self, before, user):
        '''
        Whenever a server member changes their state.
        '''
        if (user.display_name != before.display_name):
            # member update
            d = DBuser(before.id, user.guild.id)
            d["name"] = user.name
            d["nickname"] = user.nick if user.nick else user.name
            updateDBuser(d)
            await log(user.guild, "Member Updated: {}".format(before.name))

        elif user.status != before.status:
            # status update

            if str(user.status) == "offline":
                d = DBuser(before.id, user.guild.id)
                d["last-online"] = localTime().strftime("%I:%M:%S %p %Z")
                updateDBuser(d)
            
            else:
                d = DBuser(before.id, user.guild.id)
                d["last-online"] = "now"
                updateDBuser(d)


            for i in d["check-when-online"]:
                m = user.guild.get_member(i)
                embed = discord.Embed(title=f"{user.display_name} is now {str(user.status)}.", description=str(m))
                embed.add_field(name="Time", value=(localTime().strftime("%I:%M:%S %p %Z")))
                await DM("", m, embed)
                        

    @commands.Cog.listener()
    async def on_user_update(self, before, user):
        '''
        Whenever a general user changes their state.
        '''
        if (user.name != before.name):
            # user update
            POSSIBLES = DBfind(USER_COL, {"user":user.id})
            for u in POSSIBLES:
                u["name"] = user.name
                updateDBuser(u)

            await log(user.guild, "User Updated: {}".format(before.name))

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, exception):
        # When a command fails to execute
        if not (type(exception) == commands.CheckFailure or type(exception) == commands.CommandNotFound):
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)
        
        if type(exception) == commands.NoPrivateMessage:
            await reactX(ctx)
            await ctx.send("This command can only be used in a server.")
            
        elif type(exception) == commands.CheckFailure:
            await reactX(ctx)
            await ctx.send("You have insufficient permission to use this command {}".
                format(ctx.author.mention))

        elif type(exception) == commands.BadArgument:
            await reactX(ctx)
            await ctx.send(exception)

        elif type(exception) == commands.BadUnionArgument:
            await reactX(ctx)
            await ctx.send("\n".join([str(e) for e in exception.errors]))
        
        elif type(exception) == commands.NSFWChannelRequired:
            await reactX(ctx)
            await ctx.send("This command can only be used in a NSFW channel.")
            
        elif type(exception) == commands.CommandNotFound:
            await reactQuestion(ctx)
            await ctx.send("'{}' is not a valid command.".format(ctx.message.content))
        
        elif type(exception) == SyntaxError:
            await reactX(ctx)
            await ctx.send("Cosmo Error: {}".format(exception))

        else:
            await reactQuestion(ctx)
            await ctx.send("Command Error: {}".format(exception))
            
            if ctx.guild: await log(ctx.guild, "Failure: {}\nType: {}\nTraceback:```{}```".format(exception, type(exception).__name__, traceback.format_exception(type(exception), exception, exception.__traceback__)))
            else: await ctx.send("```Failure: {}\nType: {}\nTraceback:{}```".format(exception, type(exception).__name__,  traceback.format_exception(type(exception), exception, exception.__traceback__)))
            await DM(f"Failure: {exception}\n ```{traceback.format_exception(type(exception), exception, exception.__traceback__)}```", (await self.bot.application_info()).owner)


        
