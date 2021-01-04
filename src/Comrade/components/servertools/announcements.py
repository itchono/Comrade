'''
Comrade - Timed announcements
'''
import discord
from discord.ext import commands, tasks

from utils.utilities import local_time, ufil, role
from utils.checks import isServerOwner
from utils.reactions import reactOK
from utils.users import weighted_member_id_from_server, rebuild_weight_table
from db import collection


class Announcements(commands.Cog):
    '''
    Add timed announcements, delivered in the announcements channel
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.announcements = {}

        self.timedannounce.start()

    def cog_unload(self):
        self.timedannounce.cancel()

    async def dailyannounce(self, channel: discord.TextChannel):
        '''
        Daily announcement
        '''
        m = await channel.send("Good morning everyone! Today is "
                               f"{local_time().strftime('%A, %B %d (Day %j in %Y). Time is %I:%M %p %Z')}. Have a great day.")
        '''
        Daily user
        '''
        ctx = await self.bot.get_context(m)

        if luckyperson := channel.guild.get_member(
                await weighted_member_id_from_server(channel.guild)):

            collection("users").update_one(
                ufil(luckyperson, channel.guild),
                {"$inc": {"daily-weight": -1}})

            dailyrole = await role(channel.guild, "Member of the Day")

            for m in dailyrole.members:
                # remove bearer of previous daily role
                roles = m.roles
                roles.remove(dailyrole)
                await m.edit(roles=roles)
            roles = luckyperson.roles
            roles.append(dailyrole)
            await luckyperson.edit(roles=roles)

            await channel.send(
                f"Today's Daily Member is **{luckyperson.display_name}**")

            general_cog = self.bot.get_cog("General")
            await general_cog.avatar(ctx, member=luckyperson)

            await rebuild_weight_table(channel.guild)

    @tasks.loop(minutes=1.0)
    async def timedannounce(self):
        '''
        Makes an announcement
        '''
        servers = collection("servers").find()

        now = local_time()

        for s in servers:
            try:
                for a in self.announcements[s["_id"]]:

                    if (now.strftime("%H:%M") == a["time"]):
                        c = self.bot.get_channel(
                            s["channels"]["announcements"])

                        if c:
                            # daily announce
                            if hasattr(a["announcement"], "__call__"):
                                await a["announcement"](c)
                            else: 
                                await c.send(a["announcement"])
            except Exception:
                pass

    @timedannounce.before_loop
    async def build_announcement_cache(self):
        await self.bot.wait_until_ready()
        for g in self.bot.guilds:
            additonal_announcements = [
                {"server": g.id, "time": "08:00",
                 "announcement": self.dailyannounce, "owner": None}]

            if d := collection("announcements").find({"server": g.id}):
                self.announcements[g.id] = list(d) + additonal_announcements
            else:
                self.announcements[g.id] = additonal_announcements

    @commands.command()
    @commands.guild_only()
    async def addannounce(self, ctx: commands.Context, time, *, message):
        '''
        Adds an announcement to the announcement system [24 hr time].
        Each user is allowed to have a maximum of one announcement.
        '''
        announce = {
            "server": ctx.guild.id,
            "time": time, "announcement": message, "owner": ctx.author.id}

        collection("announcements").update_one(
            {"server": ctx.guild.id,
             "owner": ctx.author.id}, announce, upsert=True)

        await reactOK(ctx)
        await self.build_announcement_cache()  # rebuild cache

    @commands.command()
    @commands.guild_only()
    async def removeannounce(self, ctx: commands.Context, time, *, message):
        '''
        Removes an announcement from the announcement system
        '''
        collection("announcements").delete_one(
            {"server": ctx.guild.id, "owner": ctx.author.id})
        await reactOK(ctx)
        await self.build_announcement_cache()  # rebuild cache

    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def testannounce(self, ctx: commands.Context, time):
        '''
        Tests making an announcement
        '''
        for a in self.announcements[ctx.guild.id]:

            if (time == a["time"]):
                c = ctx.guild.get_channel(
                    collection("servers").find_one(
                        ctx.guild.id)["channels"]["announcements"])

                if hasattr(a["announcement"], "__call__"):
                    await a["announcement"](c)  # daily announce

                else:
                    await c.send(a["announcement"])
