from utils.utilities import *
from utils.mongo_interface import *


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    @commands.check(isServer)
    async def mute(self, ctx: commands.Context, target):
        '''
        Votes to mute a selected user.
        As OP: Mute the user
        '''
        u = await extractUser(ctx, target)

        if isOP(ctx):
            # direct mute
            mutedrole = await mutedRole(ctx.guild)

            if mutedrole in u.roles:
                roles = u.roles
                roles.remove(mutedrole)
                await u.edit(roles=roles)
                await ctx.send("{} was unmuted.".format(u.display_name))
            else:
                roles = u.roles
                roles.append(mutedrole)
                await u.edit(roles=roles)
                await ctx.send("{} was muted.".format(u.display_name))

                for channel in ctx.guild.channels:
                    await channel.set_permissions(mutedrole, send_messages=False)

        else:
            usr = getUser(u.id, ctx.guild.id)
            vm = usr["mute votes"]

            if not ctx.author.id in vm:
                vm.append(ctx.author.id)
                await ctx.send("Vote to mute {} added. ({} votes)".format(u.display_name, len(vm)))
            else:
                vm.remove(ctx.author.id)
                await ctx.send("Vote to mute {} removed. ({} votes)".format(u.display_name, len(vm)))

            usr["mute votes"] = vm

            updateUser(usr)
            

    @commands.command()
    @commands.check(isServer)
    async def kick(self, ctx: commands.Context, target):
        u = await extractUser(ctx, target)

        usr = getUser(u.id, ctx.guild.id)
        vk = usr["kick votes"]

        if not ctx.author.id in vk:
            vk.append(ctx.author.id)
            await ctx.send("Vote to kick {} added. ({} votes)".format(u.display_name, len(vk)))
        else:
            vk.remove(ctx.author.id)
            await ctx.send("Vote to kick {} removed. ({} votes)".format(u.display_name, len(vk)))

        usr["kick votes"] = vk

        updateUser(usr)

    @commands.check(isOP)
    async def mod(self, ctx: commands.Context, *, args):
        '''
        Moderation interface for Comrade
        '''
        args = args.split()

        pass