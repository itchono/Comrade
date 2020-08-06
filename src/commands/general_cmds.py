from utils.utilities import *

import math


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

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

    @commands.command()
    async def moststale(self, ctx: commands.Context, limit:int = None):
        '''
        Returns the top n most stale channels (default: 15%)
        '''

        channels = {}

        await ctx.trigger_typing()

        for channel in ctx.guild.text_channels:
            try:
                msg = (await channel.history(limit=1).flatten()).pop()

                t0 = UTCtoLocalTime(msg.created_at)
                difference = (localTime() - t0).days

                channels[channel.mention] = difference
            except: pass # empty channel

        if not limit: limit = math.ceil(0.15*len(channels)) # 15% of top

        top = sorted([(channels[k], k) for k in channels], reverse=True)[:limit]

        await ctx.send(f"Top {limit} most stale channels:\n" + "\n".join([f"{top.index(i) + 1}. {i[1]} ({i[0]} days)" for i in top]))

    @commands.command()
    async def news(self, ctx:commands.Context,*, content):
        '''
        Wraps a piece of text in a fancy border for news
        '''
        BORDER_TOP =    "╔═══.·:·.✧    ✦    ✧.·:·.═══╗"
        ACCENT_BORDER = "      ≻───── ⋆✩⋆ ─────≺"
        BORDER_BOTTOM = "╚═══.·:·.✧    ✦    ✧.·:·.═══╝"
        len_border = len(BORDER_TOP)

        words = content.split(" ")
        lines = []
        buffer = "" # line buffer

        while words:
            # do until the array of words is empty

            if len(words[0]) >= len_border and (max_word := words.pop(0)): words = [max_word[:len_border-2] + '-', max_word[len_border-2:]] + words

            while words and len(buffer + words[0]) < len_border: buffer += words.pop(0) + " "
            
            lines.append(buffer.strip(" ").center(len_border)) # center the text in the block after removing spaces
            buffer = ""
                       
        content = "\n".join(lines)

        c = self.bot.get_cog("Echo")

        # using monospaced font to fix spacing
        await c.echo(ctx, f"**```{BORDER_TOP}\n{ACCENT_BORDER}\n{content}\n{ACCENT_BORDER}\n{BORDER_BOTTOM}```**", str(ctx.author.id))


    



    

