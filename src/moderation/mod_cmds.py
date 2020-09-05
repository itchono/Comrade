import discord
from discord.ext import commands
from utils import *
import typing

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases = ["shutup"])
    @commands.guild_only()
    async def mute(self, ctx: commands.Context,*, member: discord.Member):
        '''
        Votes to mute a selected user.
        As OP: Mute the user
        '''
        mutedrole = await mutedRole(ctx.guild)

        if isOP(ctx):
            # direct mute

            if mutedrole in member.roles:
                roles = member.roles
                roles.remove(mutedrole)
                await member.edit(roles=roles)
                await ctx.send("{} was unmuted.".format(member.display_name))
            else:
                roles = member.roles
                roles.append(mutedrole)
                await member.edit(roles=roles)
                await ctx.send("{} was muted.".format(member.display_name))

                for channel in ctx.guild.channels:
                    await channel.set_permissions(mutedrole, send_messages=False, add_reactions=False)

        else:
            usr = DBuser(member.id, ctx.guild.id)
            vm = usr["mute-votes"]

            kickreq = DBcfgitem(ctx.guild.id, "mute-requirement")

            '''
            Dynamic mute requirement
            '''
            if type(kickreq) == str and "%" in kickreq:
                online_humans = [m for m in ctx.guild.members if (str(m.status) != "offline" and not m.bot)]
                onlinecount = len(online_humans)
                kickreq = int(float(kickreq[:-1]) / 100 * onlinecount) # rounds to nearest number of online members.
                await ctx.send(f"Threshold of {DBcfgitem(ctx.guild.id, 'mute-requirement')} equals to {kickreq} online members needed to mute.")

            if not ctx.author.id in vm:
                vm.append(ctx.author.id)
                await ctx.send("Vote to {} {} added. ({}/{} votes)".format("unmute" if mutedrole in member.roles else "mute", member.display_name, len(vm), kickreq))

                if len(vm) >= kickreq:
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

                        for channel in ctx.guild.channels:
                            await channel.set_permissions(mutedrole, send_messages=False, add_reactions=False)
                    vm = []
            else:
                vm.remove(ctx.author.id)
                await ctx.send("Vote to {} {} removed. ({}/{} votes)".format("unmute" if mutedrole in member.roles else "mute", member.display_name, len(vm), kickreq))

            usr["mute-votes"] = vm
            updateDBuser(usr)
            

    @commands.command(aliases = ["erase"])
    @commands.guild_only()
    async def kick(self, ctx: commands.Context,*, member:discord.Member):
        '''
        Votes to kick a user from the server.
        '''
        usr = DBuser(member.id, ctx.guild.id)
        vk = usr["kick-votes"]

        kickreq = DBcfgitem(ctx.guild.id, "kick-requirement")

        '''
        Dynamic kick requirement
        '''
        if type(kickreq) == str and "%" in kickreq:
            online_humans = [m for m in ctx.guild.members if (str(m.status) != "offline" and not m.bot)]
            onlinecount = len(online_humans)
            kickreq = int(float(kickreq[:-1]) / 100 * onlinecount) # rounds to nearest number of online members.
            await ctx.send(f"Threshold of {DBcfgitem(ctx.guild.id, 'kick-requirement')} equals to {kickreq} online members needed to kick.")

        if not ctx.author.id in vk:
            vk.append(ctx.author.id)
            await ctx.send("Vote to kick {} added. ({}/{} votes)".format(member.display_name, len(vk), kickreq))

            if len(vk) >= kickreq:
                await ctx.guild.kick(u)
                await ctx.send("{} was kicked.".format(u))
                vk = []
        else:
            vk.remove(ctx.author.id)
            await ctx.send("Vote to kick {} removed. ({}/{} votes)".format(member.display_name, len(vk), kickreq))

        usr["kick-votes"] = vk
        updateDBuser(usr)

    @commands.command()
    @commands.check(isOP)
    @commands.guild_only()
    async def banword(self, ctx:commands.Context, member:typing.Optional[discord.Member]=None, threshold:typing.Optional[int]=100, *, word):
        '''
        Bans a word, with an optional person to ban the word for, and a percentage similarity threshold required to trigger.
        If no member is specified, the word is banned for the whole server
        If no threshold is specified, the default threshold is 100 (exact match required)

        Use \ to escape arguments
        '''
        word = word.lstrip("\\")

        d = DBuser(member.id, ctx.guild.id) if member else DBfind_one(SERVERCFG_COL, {"_id":ctx.guild.id})
        worddict = d["banned-words"]

        if word in worddict and worddict[word] != threshold:
            del worddict[word]
            if member: 
                updateDBuser(d)
                await ctx.send(f"Word has been removed from {member.display_name}'s set of personal banned words.")
            else: 
                DBupdate(SERVERCFG_COL, {"_id":ctx.guild.id}, d)
                await ctx.send(f"Word has been removed from {ctx.guild}'s set of global banned words.")
            
        else:
            worddict[word] = threshold

            if member: 
                updateDBuser(d)
                await ctx.send(f"Word has been added to {member.display_name}'s set of personal banned words.\nActivation threshold: {threshold}%")
            else: 
                DBupdate(SERVERCFG_COL, {"_id":ctx.guild.id}, d)
                await ctx.send(f"Word has been added to {ctx.guild}'s set of global banned words.\nActivation threshold: {threshold}%")

