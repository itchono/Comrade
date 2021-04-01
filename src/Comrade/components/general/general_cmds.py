import discord
from discord.ext import commands

import typing

from utils.echo import echo

from collections import defaultdict

from utils.utilities import (get_uptime, get_host,
                             local_time, utc_to_local_time, bot_prefix)

from utils.checks import isNotThreat

from config import cfg, version
import sys


class General(commands.Cog):
    '''
    General purpose commands for checking on the status of the bot,
    and various utilites like fetching avatars.
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.last_deleted = defaultdict(lambda: None)
        self.last_edited = defaultdict(lambda: None)

    @commands.command()
    async def status(self, ctx: commands.Context):
        '''
        Shows the current status of the bot
        '''
        await ctx.send(f"**Uptime**: {round(get_uptime(), 1)}s\n"
                       f"**Version**: {version}\n"
                       f"Currently Connected to **{len(self.bot.guilds)}** "
                       f"server(s)\n**Host**: {get_host()}\n"
                       f"**API Latency**: {round(self.bot.latency, 4)}s\n"
                       f"Running discord.py version {discord.__version__}")

    @commands.command()
    async def dm(self, ctx: commands.Context, user:
                 typing.Union[discord.Member, discord.User] = None,
                 *, message: str):
        '''
        Sends a direct message to a given user via the bot
        '''
        await user.send(message)

    @commands.command()
    async def dateof(self, ctx: commands.Context, *, thing: discord.Object):
        '''
        Gets the creation time of basically any Discord object.
        '''
        await ctx.send(f"That was created on "
                       f"{utc_to_local_time(thing.created_at).strftime('%B %d %Y at %I:%M:%S.%f %p %Z')}")

    @commands.command(aliases=["lastmsg", "staleness"])
    @commands.guild_only()
    async def lastmessage(self, ctx: commands.Context,
                          channel: discord.TextChannel):
        '''
        Checks when the last message was sent in a channel
        '''
        msg = (await channel.history(limit=1).flatten()).pop()

        t0 = utc_to_local_time(msg.created_at)
        difference = (local_time() - t0).days

        await ctx.send(f"Last message in {channel.mention} was sent on"
                       f" {t0.strftime('%B %d %Y at %I:%M:%S %p %Z')} by "
                       f"`{msg.author.display_name}` ({difference} days ago.)")

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context):
        '''
        Gets information about the server.
        '''
        e = discord.Embed(colour=ctx.guild.roles[-1].colour)
        e.set_thumbnail(url=ctx.guild.icon_url)
        e.set_author(name=f"Information for {ctx.guild.name}",
                     icon_url=ctx.guild.icon_url)

        e.add_field(name="Time of Creation",
                    value=utc_to_local_time(ctx.guild.created_at).strftime('%B %d %Y at %I:%M:%S %p %Z'),
                    inline=False)

        e.add_field(name="Text Channels",
                    value=len(ctx.guild.text_channels))
        e.add_field(name="Voice Channels",
                    value=len(ctx.guild.voice_channels))
        e.add_field(name="Channel Categories",
                    value=len(ctx.guild.categories))

        e.add_field(name="Total Members",
                    value=ctx.guild.member_count)
        e.add_field(name="Human Members",
                    value=len([i for i in ctx.guild.members if not i.bot]))

        e.add_field(name="Emojis",
                    value=len(ctx.guild.emojis))
        e.add_field(name="Roles",
                    value=len(ctx.guild.roles))

        e.add_field(name="Server Icon", value=f"[Link]({ctx.guild.icon_url})")
        e.add_field(name="Owner", value=ctx.guild.owner.mention)

        e.set_footer(text=f"ID: {ctx.guild.id}")
        await ctx.send(embed=e)

    @commands.command(aliases=["pfp"])
    async def avatar(self, ctx: commands.Context, *,
                     member: typing.Union[discord.Member,
                                          discord.User] = None):
        '''
        Displays the avatar of a target user, or yourself by default
        Made by Slyflare, PhtephenLuu
        '''
        if not member:
            member = ctx.author

        col = member.colour if type(member) == discord.Member \
            else discord.Color.dark_blue()

        a = discord.Embed(color=col,
                          title=f"{member.display_name}'s Avatar",
                          url=str(member.avatar_url_as(static_format="png")))

        a.set_image(url=member.avatar_url)
        await ctx.send(embed=a)

    @commands.command()
    @commands.guild_only()
    async def emoji(self, ctx: commands.Context):
        '''
        Shows all emoji in the server
        '''
        emoji = "".join([str(e) for e in ctx.guild.emojis])
        await ctx.send(f"{ctx.guild.name} has "
                       f"{len(ctx.guild.emojis)} emojis:\n{emoji}")

    @commands.command()
    @commands.check(isNotThreat())
    async def clear(self, ctx: commands.Context, amount: typing.Optional[int] = 50):
        '''
        Clears bot commands (server-only) and messages
        from bot in the last 50 messages or otherwise specified
        '''
        if ctx.guild:
            def check(message):
                return (message.content and message.content.startswith(bot_prefix)) or \
                        message.author == self.bot.user
            await ctx.channel.purge(check=check, bulk=True, limit=amount)
        else:
            async for msg in ctx.channel.history(limit=amount):
                if msg.author == self.bot.user:
                    await msg.delete()

    @commands.command()
    async def getlog(self, ctx: commands.Context):
        '''
        Uploads Comrade's log file for analysis
        '''
        with open("comrade.log", "rb") as f:
            await ctx.send(file=discord.File(f, filename="comrade_log.txt"))

    @commands.command()
    async def website(self, ctx: commands.Context):
        '''
        Pastes in Comrade's website, if the owner configured it
        '''
        if url := cfg["Hosting"]["host-url"]:
            await ctx.send(url)
        else:
            await ctx.send("The owner has not configured a hosting website")

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx: commands.Context):
        '''
        Restarts the bot on the remote host
        '''
        await ctx.send("Restarting...")
        with open("restart.cfg", "w") as f:
            f.write(str(ctx.channel.id))
            # pointer for bot restart
        await self.bot.change_presence(status=discord.Status.offline)
        await self.bot.logout()
        sys.exit(0)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.last_deleted[message.channel.id] = message

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        '''
        When a message is deleted
        '''
        if msg := payload.cached_message:
            if msg.guild and not msg.author.bot:
                if msg.mentions: await msg.channel.send(f":rotating_light: PING POLICE :rotating_light:\n{msg.author.mention} deleted a message which pinged the following user(s): {', '.join(['`' + m.display_name + '`' for m in msg.mentions])}")
                elif msg.role_mentions: await msg.channel.send(f":rotating_light: PING POLICE :rotating_light:\n{msg.author.mention} deleted a message which pinged the following role(s): {', '.join(['`' + m.name + '`' for m in msg.role_mentions])}")


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        self.last_edited[after.channel.id] = (before, after)

    @commands.command()
    async def deleted(self, ctx: commands.Context):
        '''
        Retrieves the last message deleted in the channel
        '''
        if msg := self.last_deleted[ctx.channel.id]:
            await echo(ctx, member=msg.author, content=msg.content,
                       file=msg.attachments[0] if msg.attachments else None,
                       embed=msg.embeds[0] if msg.embeds else None)
            self.last_deleted[ctx.channel.id] = None
        else:
            await ctx.send("No known deleted messages")

    @commands.command()
    async def edited(self, ctx: commands.Context):
        '''
        Retrieves the last message edited in the channel
        '''
        if msg := self.last_edited[ctx.channel.id]:
            before, after = msg
            await echo(ctx, member=before.author, content=before.content,
                       file=before.attachments[0] if before.attachments else None,
                       embed=before.embeds[0] if before.embeds else None)
            await ctx.send(after.jump_url)
            self.last_edited[ctx.channel.id] = None
        else:
            await ctx.send("No known edited messages")
