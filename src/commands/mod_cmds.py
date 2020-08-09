from utils.utilities import *



class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command()
    @commands.guild_only()
    async def mute(self, ctx: commands.Context, member: discord.Member):
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
            

    @commands.command()
    @commands.guild_only()
    async def kick(self, ctx: commands.Context, member:discord.Member):
        '''
        Votes to kick a user from the server.
        '''
        usr = DBuser(member.id, ctx.guild.id)
        vk = usr["kick-votes"]

        kickreq = DBcfgitem(ctx.guild.id, "kick-requirement")

        '''
        Dynamic kick requirement
        '''

        online_humans = [m for m in ctx.guild.members if (str(m.status) != "offline" and not m.bot)]
        onlinecount = len(online_humans)


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

    # DEFUNCT
    # @commands.command()
    # @commands.check(isOP)
    # @commands.guild_only()
    # async def mod(self, ctx: commands.Context, target, listname, operation=None, value=None):
    #     '''
    #     Changes a value in a user's configuration. Various possible operations
    #     add: Add element to list
    #     remove: Remove an element from list (specify value)
    #     pop: Remove last element from list (no value specification needed)
    #     set: Set numerical type
    #     toggle: Switch a boolean
    #     '''
    #     if u := await getUser(ctx, target):

    #         if operation in {"add", "remove", "pop"}:
    #             if l := getuserList(u.id, ctx.guild.id, listname):
    #                 if operation == "add": 
    #                     l.append(value)
    #                     await reactOK(ctx)
                    
    #                 elif operation == "remove":
    #                     try: 
    #                         l.remove(value)
    #                         await reactOK(ctx)
    #                     except: await delSend(ctx, "Could not find element {} in list.".format(value))
    #                 else:
    #                     ret = l.pop()
    #                     await delSend(ctx, "Popped element {}".format(ret))

    #                 updateuserList(u.id, ctx.guild.id, listname, l)

    #         elif operation == "set":
    #             try:
    #                 result = setnum(u.id, ctx.guild.id, listname, value)
    #                 await reactOK(ctx)
    #                 await ctx.send("{} is now set to {}".format(listname, result))
    #             except:
    #                 await delSend(ctx, "Invalid operation.")

    #         elif operation == "toggle":
    #             try:
    #                 result = togglebool(u.id, ctx.guild.id, listname)
    #                 await reactOK(ctx)
    #                 await ctx.send("{} is now set to {}".format(listname, result))
    #             except:
    #                 await delSend(ctx, "Invalid operation.")
    #         else:
    #             await reactQuestion(ctx)
    #             await delSend(ctx, "Unrecognized operation: {}".format(operation))