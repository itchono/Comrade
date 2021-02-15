from utils.reactions import reactOK
import discord
from discord.ext import commands

import typing
import datetime
import re

from db import collection
from utils.utilities import ufil, local_time, bot_prefix, utc_to_local_time
from utils.users import random_member_from_server, weight_table
from utils.checks import isOP
from utils.databases import new_user
from utils.logger import logger


class Users(commands.Cog):
    '''
    A set of commands for inspecting and working with
    Discord users
    '''

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(aliases=["profile"])
    async def userinfo(self, ctx: commands.Context, *,
                       member: typing.Union[discord.Member,
                                            discord.User] = None):
        '''
        Displays User Information of said person
        Developed by Slyflare
        '''
        if not member:
            member = ctx.author

        e = discord.Embed(colour=member.colour)
        e.set_author(name=f"{member.display_name} ({member})",
                     icon_url=member.avatar_url)
        e.set_thumbnail(url=member.avatar_url)
        e.set_footer(text=f"ID: {member.id}")

        e.add_field(name="Is Human",
                    value=not member.bot)

        e.add_field(name="Account Created",
                    value=utc_to_local_time(member.created_at).strftime(
                        '%B %d %Y at %I:%M:%S %p %Z'), inline=False)

        if ctx.guild:
            user_information = collection(
                "users").find_one(ufil(member))

            e.add_field(name="Joined Server",
                        value=utc_to_local_time(member.joined_at).strftime(
                            '%B %d %Y at %I:%M:%S %p %Z'), inline=False)

            if w := user_information["daily-weight"]:
                e.add_field(name="Daily Weight", value=w)

            if w := user_information["OP"]:
                e.add_field(name="OP", value=w)

            if (w := user_information["moderation"]["threat-level"]):
                e.add_field(name="Threat Level", value=w)

            if w := user_information["identity"]:
                e.add_field(name="Identity", value=w)
            else:
                e.add_field(name="Identity", value="Unknown")

            e.add_field(name="Status",
                        value=member.status)

            e.add_field(name="On Mobile",
                        value=member.is_on_mobile())

            if w := user_information["last-online"]:
                e.add_field(name="Last Online",
                            value=w)

            # Show stack of roles
            e.add_field(name=f"Roles ({len(member.roles)})",
                        value="\n".join([
                            role.mention for role in member.roles]),
                        inline=False)

        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def rolluser(self, ctx: commands.Context):
        '''
        Rolls a random user in the server, either weighted or unweighted
        '''
        mem = random_member_from_server(ctx.guild)
        await self.userinfo(ctx, member=mem)

    @commands.command()
    @commands.guild_only()
    async def track(self, ctx: commands.Context, *, member: discord.Member):
        '''
        Makes it so that when a user changes status, you are notified.
        This command is a toggle.
        '''
        notifiees = collection(
            "users").find_one(ufil(member))["notify-status"]

        if ctx.author.id in notifiees:
            collection("users").update_one(
                ufil(member),
                {"$pull": {"notify-status": ctx.author.id}})
            await ctx.send(
                f"You will no longer be notified by when {member.display_name} changes their status.")
        else:
            collection("users").update_one(
                ufil(member),
                {"$push": {"notify-status": ctx.author.id}})
            await ctx.send(
                f"You will now be notified by when {member.display_name} changes their status.")

    @commands.command()
    @commands.guild_only()
    async def identity(self, ctx: commands.Context,
                       member: typing.Optional[discord.Member] = None, *,
                       name: typing.Optional[str] = None):
        '''
        Looks up user with real identity, or sets their identity.
        '''
        if name and member:
            # Case: assign name to member
            collection(
                "users").update_one(
                    ufil(member),
                    {"$set": {"identity": name}})
            await reactOK(ctx)
        elif name and (real_user := collection(
            "users").find_one(
                {"identity": re.compile('^' + name + '$', re.IGNORECASE)})):
            # Case: find unknown user
            user = ctx.guild.get_member(real_user["user"])
            await self.userinfo(ctx, member=user)

        elif member:
            await ctx.send(collection(
                "users").find_one(ufil(member))["identity"])
        else:
            await ctx.send("No identity listed")

    @commands.command()
    @commands.guild_only()
    async def requiem(self, ctx: commands.Context,
                      day: int = 30, trim=False):
        '''
        Generates a list of users who have not talked in the past x days
        '''
        threshold = datetime.datetime.now() - datetime.timedelta(day)

        active_author_ids = set()

        for channel in ctx.guild.text_channels:

            active_ids_in_channel = await channel.history(
                limit=None, after=threshold).filter(
                    lambda msg: msg.type == discord.MessageType.default
            ).map(lambda msg: msg.author.id).flatten()

            active_author_ids += set(active_ids_in_channel)

        inactive_author_ids = set(
            [member.id for member in ctx.guild.members]) - active_author_ids

        await ctx.send(
            f"{len(inactive_author_ids)} members detected to have not posted in the past {day} days.")

        OP = isOP()(ctx)  # check before trimming

        s = "```"
        for member in [
                await ctx.guild.get_member(
                    idd) for idd in inactive_author_ids]:
            s += member.display_name + "\n"

            if trim and OP:
                collection("users").update_one(
                    ufil(member), {"$set": {"daily-weight": 0}})
        s += "```"
        await ctx.send(s)

        if trim:
            await ctx.send("Users above have been removed from the daily member pool.")

    @commands.command()
    @commands.guild_only()
    async def modchance(self, ctx,
                        member: typing.Optional[discord.Member] = None):
        '''
        Shows the chance of a user to be member of the day [MoD]
        '''
        if not member:
            member = ctx.author

        _, weights = weight_table(ctx.guild)

        sum_of_weights = sum(weights)

        count = collection(
            "users").find_one(ufil(member))["daily-weight"]

        if sum_of_weights > 0:
            await ctx.send(
                f"{member.display_name}'s chance of being rolled tomorrow is {count}/{sum_of_weights} ({round(count/sum_of_weights * 100, 2)}%)")
        else:
            await ctx.send("Daily weight cache is currently unavailable (may be being rebuilt).")

    @commands.command()
    @commands.guild_only()
    async def modweights(self, ctx):
        '''
        Shows relative weights of daily member table.
        '''
        member_ids, weights = weight_table(ctx.guild)

        pg = commands.Paginator()

        for i in range(len(weights)):
            pg.add_line(
                f"{ctx.guild.get_member(member_ids[i]).display_name}: {weights[i]}")
        pg.add_line(f"Total: {sum(weights)} entries.")

        for page in pg.pages:
            await ctx.send(page)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        '''
        When a member joins the server.
        '''
        announcements_channel_id = collection(
            "servers").find_one(
                member.guild.id)["channels"]["announcements"]
        if channel := member.guild.get_channel(announcements_channel_id):
            await channel.send(f"Welcome {member.display_name}!")
        logger.info("Member join")

        collection("users").insert_one(new_user(member))
        # New user entry in DB

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        '''
        When a member leaves the server
        '''
        announcements_channel_id = collection(
            "servers").find_one(member.guild.id)["channels"]["announcements"]

        if channel := member.guild.get_channel(announcements_channel_id):

            await channel.send(f":door: {member.display_name} has left.")
        logger.info("Member leave")

        collection("users").delete_one(ufil(member))
        # Delete DB entry

    @commands.Cog.listener()
    async def on_member_update(self,
                               before: discord.Member, after: discord.Member):
        '''
        Whenever a server member changes their state.
        '''
        if after.status != before.status:
            # status update

            if str(after.status) == "offline":

                collection("users").update_one(
                    ufil(after),
                    {"$set": {
                        "last-online":
                        local_time().strftime("%I:%M:%S %p %Z")}})
            else:
                collection("users").update_one(
                    ufil(after),
                    {"$set": {
                        "last-online": "Now"}})

            for mem_id in collection(
                    "users").find_one(
                        ufil(after))["notify-status"]:
                mem = after.guild.get_member(mem_id)

                embed = discord.Embed(color=0xd7342a,
                    description=
                    f"{str(before.status)} -> {str(after.status)} @ {local_time().strftime('%I:%M:%S %p %Z')}")

                embed.set_author(
                    name=
                    f"{after.display_name} ({str(after)}) is now {str(after.status)}.",
                    icon_url=after.avatar_url)
                embed.set_footer(
                    text=
                    f"To unsubscribe, type [{bot_prefix}track {after.display_name}] in {after.guild.name}")

                await mem.send(embed=embed)
