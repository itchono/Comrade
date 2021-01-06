import discord
from discord.ext import commands

from ast import literal_eval
import typing

from db import collection
from utils.checks import isServerOwner
from utils.reactions import reactOK, reactX
from utils.utilities import ufil
from utils.databases import rebuild_server_cfgs


class Databases(commands.Cog):
    '''
    Server-side configuration of Comrade's Databases.
    '''

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def setchannel(self, ctx: commands.Context,
                         channel_name: str,
                         channel: typing.Union[
                             discord.TextChannel,
                             discord.CategoryChannel] = None):
        '''
        Sets a channel with the given name into the Database.
        Leave channel blank to unset (delete)
        '''
        if channel_name not in ["vault", "announcements", "log", "custom"]:
            await reactX(ctx)
            return

        try:
            if channel:
                collection("servers").update_one(
                    {"_id": ctx.guild.id},
                    {"$set": {f"channels.{channel_name}": channel.id}})

            else:
                collection("servers").update_one(
                    {"_id": ctx.guild.id},
                    {"$set": {f"channels.{channel_name}": 0}})
        except Exception as ex:
            await ctx.send(f"Error: {ex}")
            return

        await reactOK(ctx)

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def channelmappings(self, ctx: commands.Context):
        '''
        View database channel mappings
        '''
        server_cfg = collection("servers").find_one({"_id": ctx.guild.id})

        s = ""

        for channel_name in server_cfg["channels"]:
            if channel := self.bot.get_channel(
                    server_cfg["channels"][channel_name]):
                s += f"{channel_name}: {channel.mention}\n"
            else:
                s += f"{channel_name}: Unassigned\n"

        await ctx.send(s)

    @commands.group(name="cfg", aliases=["config", "set"])
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def configure(self, ctx: commands.Context):
        '''
        Alters configuration settings
        '''
        if ctx.invoked_subcommand is None:
            await ctx.send("These operations are quite dangerous."
                           "Proceed with caution.")

    @configure.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def user(self, ctx: commands.Context,
                   member: discord.Member, index: str, value=None):
        '''
        Modifies a value in the user database.
        Leave value as none to delete field.
        Access nested fields using dot notation
        ex. {"sandwich": {"bread":rye}}
        >>> "sandwich.bread" would be the index
        '''

        if value is None:
            try:
                collection("users").update_one(
                    ufil(member),
                    {"$unset": {index: ""}}
                )
            except Exception as ex:
                await ctx.send(f"Error: {ex}")

        else:
            try:
                collection("users").update_one(
                    ufil(member),
                    {"$set": {index: literal_eval(value)}}
                )
            except Exception as ex:
                await ctx.send(f"Error: {ex}")

        await reactOK(ctx)

    @configure.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def allusers(self, ctx: commands.Context,
                       index: str, value=None):
        '''
        Modifies a value in every user's config in this server.
        Leave value as none to delete field.
        Access nested fields using dot notation
        ex. {"sandwich": {"bread":rye}}
        >>> "sandwich.bread" would be the index
        '''

        if value is None:
            try:
                collection("users").update_many(
                    {"server": ctx.guild.id},
                    {"$unset": {index: ""}}
                )
            except Exception as ex:
                await ctx.send(f"Error: {ex}")

        else:
            try:
                collection("users").update_many(
                    {"server": ctx.guild.id},
                    {"$set": {index: literal_eval(value)}}
                )
            except Exception as ex:
                await ctx.send(f"Error: {ex}")

        await reactOK(ctx)

    @configure.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def server(self, ctx: commands.Context,
                     index: str, value=None):
        '''
        Modifies a value in the server database.
        Leave value as none to delete field.
        Access nested fields using dot notation
        ex. {"sandwich": {"bread":rye}}
        >>> "sandwich.bread" would be the index
        '''

        if value is None:
            try:
                collection("servers").update_one(
                    {"_id": ctx.guild.id},
                    {"$unset": {index: ""}}
                )
            except Exception as ex:
                await ctx.send(f"Error: {ex}")

        else:
            try:
                collection("servers").update_one(
                    {"_id": ctx.guild.id},
                    {"$set": {index: literal_eval(value)}}
                )
            except Exception as ex:
                await ctx.send(f"Error: {ex}")

        await reactOK(ctx)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        '''
        When the bot joins a server.
        '''
        rebuild_server_cfgs(self.bot.guilds)
        # Rebuild server cfgs

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild):
        '''
        When the bot leaves a server.
        '''
        pass
        # I've been kicked etc
