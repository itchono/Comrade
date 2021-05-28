import discord
from discord.ext import commands
import typing

from utils.checks import isOP, op_list, threat_list, isServerOwner, isNotThreat
from utils.utilities import role, ufil
from db import collection
from config import cfg
from utils.logger import logger


def dynamic_threshold(guild, threshold) -> int:
    '''
    Required threshold, rounded down to nearest int
    threshold: integer percentage
    '''
    dec = threshold / 100
    thresh = dec * len(
        [m for m in guild.members if (
            str(m.status) != "offline" and not m.bot)])

    return int(thresh)


async def zahando(channel: discord.TextChannel,
                  num: int = 20,
                  user: discord.User = None):
    '''
    erases a set number of messages in a context (Default 20)
    '''
    if user:
        await channel.purge(limit=num,
                            check=lambda m: m.author == user)
    else:
        await channel.purge(limit=num)

class Moderation(commands.Cog):
    '''
    Moderation commands for the bot.
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_typing(self, channel, user, when):
        '''
        Prepare moderation filters
        '''
        # If user is a threat, raise shield

    @commands.command()
    @commands.guild_only()
    async def mute(self, ctx: commands.Context, *, member: discord.Member):
        '''
        Votes to mute a selected user.
        As OP: Mute the user
        '''
        OP = isOP()(ctx)

        mutedrole = await role(ctx.guild, "Comrade-Mute")

        user_info = collection("users").find_one(ufil(member))
        vm = user_info["moderation"]["mute-votes"]

        mutereq = collection(
            "servers").find_one(ctx.guild.id)["thresholds"]["mute"]

        '''
        Dynamic mute requirement support
        '''
        if type(mutereq) == str and "%" in mutereq:
            mutereq = dynamic_threshold(
                ctx.guild, float(mutereq.strip("%").strip()))
            await ctx.send(
                f"Dynamic mute threshold equals to {mutereq} online members needed to mute.")

        decision = "unmute" if mutedrole in member.roles else "mute"

        if ctx.author.id not in vm or OP:

            if not OP:
                collection("users").update_one(
                    ufil(member),
                    {"$push": {"moderation.mute-votes": ctx.author.id}})

                await ctx.send(
                    f"Vote to {decision} {member.display_name} added. ({len(vm) + 1}/{mutereq} votes)")

            if len(vm) + 1 >= mutereq or OP:
                if mutedrole in member.roles:
                    roles = member.roles
                    roles.remove(mutedrole)
                    await member.edit(roles=roles)
                    await ctx.send(f"{member.display_name} was unmuted.")
                else:
                    roles = member.roles
                    roles.append(mutedrole)
                    await member.edit(roles=roles)
                    await ctx.send(f"{member.display_name} was muted.")

                    # Update perms for muted role
                    for channel in ctx.guild.channels:
                        await channel.set_permissions(
                            mutedrole,
                            send_messages=False, add_reactions=False)

                collection("users").update_one(
                    ufil(member),
                    {"$set": {"moderation.mute-votes": []}})
        else:
            collection("users").update_one(
                    ufil(member),
                    {"$pull": {"moderation.mute-votes": ctx.author.id}})

            await ctx.send(
                    f"Vote to {decision} {member.display_name} added. ({len(vm) - 1}/{mutereq} votes)")

    @commands.command()
    @commands.guild_only()
    async def kick(self, ctx: commands.Context, *, member: discord.Member):
        '''
        Votes to kick a user from the server.
        '''
        user_info = collection("users").find_one(ufil(member))
        vk = user_info["moderation"]["kick-votes"]

        kickreq = collection(
            "servers").find_one(ctx.guild.id)["thresholds"]["kick"]

        '''
        Dynamic kick requirement
        '''
        if type(kickreq) == str and "%" in kickreq:
            kickreq = dynamic_threshold(
                ctx.guild, float(kickreq.strip("%").strip()))
            await ctx.send(
                f"Dynamic mute threshold equals to {kickreq} online members needed to mute.")

        if ctx.author.id not in vk:
            collection("users").update_one(
                        ufil(member),
                        {"$push": {"moderation.kick-votes": ctx.author.id}})
            await ctx.send(f"Vote to kick {member.display_name} added. ({len(vk) + 1}/{kickreq} votes)")

            if len(vk) + 1 >= kickreq:

                collection("users").update_one(
                    ufil(member),
                    {"$set": {"moderation.kick-votes": []}})
                await ctx.guild.kick(member)
                await ctx.send(f"{member.display_name} was kicked.")

        else:
            collection("users").update_one(
                        ufil(member),
                        {"$pull": {"moderation.kick-votes": ctx.author.id}})
            await ctx.send(f"Vote to kick {member.display_name} removed. ({len(vk) - 1}/{kickreq} votes)")

    @commands.command()
    @commands.check(isOP())
    @commands.guild_only()
    async def banword(self, ctx: commands.Context,
                      member: typing.Optional[discord.Member] = None,
                      threshold: typing.Optional[int] = 100, *, word):
        '''
        Bans a word, with an optional person to ban the word for,
        and a percentage similarity threshold required to trigger.
        If no member is specified, the word is banned for the whole server
        If no threshold is specified, the default threshold is 100
        (exact match required)
        Use \\ to escape arguments
        '''
        word = word.lstrip("\\")  # strip \

        if member:
            user_cfg = collection("users").find_one(ufil(member))

            if word in user_cfg["moderation"]["banned-words"]:
                collection("users").update_one(
                    ufil(member),
                    {"$unset": {f"moderation.banned-words.{word}": ""}})
                await ctx.send(
                    f"Word has been removed from {member.display_name}'s set of personal banned words.")

            else:
                collection("users").update_one(
                    ufil(member),
                    {"$set": {f"moderation.banned-words.{word}": threshold}})
                await ctx.send(
                    f"Word has been added to {member.display_name}'s set of personal banned words.\nActivation threshold: {threshold}%")

        else:
            server_cfg = collection("servers").find_one(ctx.guild.id)

            if word in server_cfg["global-banned-words"]:
                collection("servers").update_one(
                    {"_id": ctx.guild.id},
                    {"$unset": {f"global-banned-words.{word}": ""}})
                await ctx.send(
                    f"Word has been removed from {ctx.guild.name}'s global banned words.")

            else:
                collection("servers").update_one(
                    {"_id": ctx.guild.id},
                    {"$set": {f"global-banned-words.{word}": threshold}})
                await ctx.send(
                    f"Word has been added to {member.display_name}'s set of personal banned words.\nActivation threshold: {threshold}%")

    @commands.command()
    @commands.check_any(commands.check(isOP()), isServerOwner())
    async def op(self, ctx, *, member: discord.Member):
        '''
        OPs a member
        '''
        collection("users").update_one(ufil(member), {"$set": {"OP": True}})
        op_list.cache_clear()
        await ctx.send(f"{member.display_name} is now OP.")

    @commands.command()
    @commands.check(isOP())
    async def deop(self, ctx, *, member: discord.Member):
        '''
        de-OPs a member
        '''
        collection("users").update_one(ufil(member), {"$set": {"OP": False}})
        op_list.cache_clear()
        await ctx.send(f"{member.display_name} is no longer OP.")

    @commands.command()
    @commands.check(isOP())
    async def threat(self, ctx, level: int, *, member: discord.Member):
        '''
        sets a member's threat level
        '''
        collection(
            "users").update_one(
                ufil(member), {"$set": {"moderation.threat-level": level}})
        threat_list.cache_clear()
        assert member.id in threat_list(ctx.guild.id, level)

        await ctx.send(f"{member.display_name} is now threat level `{level}`")

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if not message.author.bot and message.guild and \
               "ZA HANDO" in message.content:
            args = (message.content.lower()).split()
            amount = 20

            if len(args) > 2 and args[2].isnumeric():
                amount = int(args[2])

            if not isNotThreat()(await self.bot.get_context(message)):
                await message.channel.send("Nah")
                return

            if amount > 200 and not isOP()(await self.bot.get_context(message)):
                await message.channel.send("No")
            else:
                duration = collection(
                    "servers").find_one(
                        message.guild.id)["durations"]["zahando"]

                froom = "from " + str(message.mentions[0]) if message.mentions else ""

                m = await message.channel.send(
                    f"React with '✋' to purge the channel of {amount} messages {froom}. You have **{duration} seconds** to vote.",
                    delete_after=duration)

                await m.add_reaction("✋")

                voted = [message.author.id]

                op = isOP()(await self.bot.get_context(message))

                def check(reaction, user):

                    voted_already = user.id in voted
                    voted.append(user.id)
                    return reaction.emoji == "✋" and not user.bot and (
                            (reaction.message.id == m.id and not voted_already)
                            or cfg["Settings"]["development-mode"] == "True"
                            or op)

                await self.bot.wait_for(
                    "reaction_add", check=check, timeout=duration)

                await zahando(
                    message.channel, amount, message.mentions[0] if message.mentions else None)

                logger.info(f"ZA HANDO performed by user {message.author.id}")
