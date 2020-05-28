from utils.utilities import *
from utils.mongo_interface import *


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def mute(self, ctx: commands.Context, target):
        '''
        Votes to mute a selected user
        '''

    @commands.command()
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