from utils.utilities import *
from utils.mongo_interface import *


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def version(self, ctx: commands.Context):
        '''
        Logs version of the bot.
        '''
        await ctx.send("Comrade is running version: {}".format(VERSION))

    @commands.command()
    async def status(self, ctx: commands.Context):
        '''
        Shows the current status of the bot
        '''
        s = "Uptime: {:.2f} s\n".format(time.perf_counter())
        s += "Version: {}\n".format(VERSION)
        s += "Currently connected to {} server(s)\n".format(len(self.bot.guilds))
        s += "Latency: {:.4f}s\n".format(self.bot.latency)
        
        await ctx.send(s)

    @commands.command()
    async def host(self, ctx: commands.Context):
        '''
        Returns name of host machine.
        '''
        await ctx.send("Comrade is currently hosted from: {}. Local time: {}".format(getHost(), localTime().strftime("%I:%M:%S %p %Z")))

    @commands.command()
    @commands.guild_only()
    async def clearcommands(self, ctx:commands.Context):
        '''
        Cleans up commands from sent from users in a channel.
        '''
        await ctx.channel.purge(check=isCommand, bulk=True)

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    async def shutdown(self, ctx:commands.Context):
        '''
        Logs out the user.
        '''
        await self.bot.logout()

    @commands.command()
    @commands.check(isNotThreat())
    async def dmUser(self, ctx: commands.Context, target, * , message:str):
        '''
        DM given user
        Made by vdoubleu
        '''
        if u := await extractUser(ctx, target):
            await DM(message, u, discord.Embed(title="", description = "Sent by {}".format(ctx.author)))
            await ctx.send("DM sent to {}".format(target), delete_after=10)

    @commands.command()
    async def msgInfo(self, ctx: commands.Context, msgid):
        '''
        Gets information about a specific message given an ID.
        '''
        msg = await ctx.channel.fetch_message(msgid)
        await ctx.send("Author: {}".format(msg.author))

    @commands.command()
    async def dateof(self, ctx: commands.Context,*, thing: typing.Union[discord.TextChannel, discord.User, discord.VoiceChannel, discord.Message]):
        '''
        Gets the creation time of a Channel, User, or Message.
        '''
        await ctx.send(f"{thing} was created on {UTCtoLocalTime(thing.created_at).strftime('%B %m %Y at %I:%M:%S %p %Z')}")

    @commands.command()
    async def staleness(self, ctx: commands.Context, channel: discord.TextChannel):
        '''
        Checks when the last message was sent in a channel
        '''
        msg = (await channel.history(limit=1).flatten()).pop()

        t0 = UTCtoLocalTime(msg.created_at)
        difference = (localTime() - t0).days

        await ctx.send(f"Last message in {channel.mention} was sent on {t0.strftime('%B %m %Y at %I:%M:%S %p %Z')} by `{msg.author.display_name}` ({difference} days ago.)")

    @commands.command(name = "list")
    @commands.guild_only()
    async def customlist(self, ctx, operation, title=None, value=None):
        '''
        Displays a lists, or adds.

        Commands: "make", "makefrom", "add", "remove", "show", "all"
        '''
        if operation in {"make", "makefrom", "add", "remove", "show", "all"}:

            if operation == "make":
                l = []
                updatecustomList(ctx.guild.id, title, l)
                await reactOK(ctx)
                
            elif operation == "makefrom":
                try:
                    msg = await commands.MessageConverter().convert(ctx, value)

                    l = []

                    for rxn in msg.reactions: l += [i.display_name for i in await rxn.users().flatten()]
                    
                    updatecustomList(ctx.guild.id, title, l)
                    await reactOK(ctx)
                
                except:
                    await ctx.send("Please specify a message to base list from.")

            elif operation == "show":
                l = getcustomList(ctx.guild.id, title)
                if l is not None:
                    await ctx.send("{}:\n{}".format(title, l))
                else:
                    await delSend(ctx, "List not found.")
            elif operation == "add":
                l = getcustomList(ctx.guild.id, title)
                if l is not None:
                    l.append(value)
                    updatecustomList(ctx.guild.id, title, l)
                    await reactOK(ctx)
                else:
                    await delSend(ctx, "List not found.")

            elif operation == "remove":
                l = getcustomList(ctx.guild.id, title)
                if l is not None:
                    try:
                        l.remove(value)
                        updatecustomList(ctx.guild.id, title, l)
                        await reactOK(ctx)
                    except:
                        await delSend(ctx, "Element {} not found.".format(value))
                else:
                    await delSend(ctx, "List not found.")

            elif operation == "all":
                await ctx.send("{}".format([i["name"] for i in listcustomLists(ctx.guild.id)]))



    

