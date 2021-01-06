# message trigger handler

import discord
from discord.ext import commands

from db import collection
from utils.reactions import reactOK, reactX
from utils.users import random_member_from_server
from utils.checks import isNotThreat
from utils.utilities import is_url


async def process_triggers(message: discord.message):
    '''
    Processes message triggers for a single message
    '''
    if message.guild and (t := collection("triggers").find_one(
        {"server": message.guild.id,
         "trigger": message.content.lower()})):
        await message.channel.send(t["message"])


class MessageTriggers(commands.Cog):
    '''
    Set the bot to say something whenever you type a certain
    message in chat.
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(aliases=["trig"])
    @commands.guild_only()
    async def addtrigger(self, ctx: commands.Context,
                         trigger: str, *, message):
        '''
        Add a message trigger
        '''
        if t := collection("triggers").find_one(
                {"server": ctx.guild.id, "trigger": trigger}):
            # Ensure no dupes in a single server
            auth = ctx.guild.get_member(t["user"])
            await reactX(ctx)
            await ctx.send(
                f"Trigger for `{trigger}` already exists (from {auth.display_name})")
            return

        trig = {
            "server": ctx.guild.id,
            "trigger": trigger,
            "message": message,
            "user": ctx.author.id

        }
        collection("triggers").insert_one(trig)
        await reactOK(ctx)

    @commands.command()
    @commands.guild_only()
    async def trigger(self, ctx: commands.Context, trigger: str):
        '''
        Send a trigger, and get information about the author
        '''
        if t := collection("triggers").find_one(
                {"server": ctx.guild.id, "trigger": trigger}):
            # Ensure no dupes in a single server
            auth = ctx.guild.get_member(t["user"])

            await process_triggers(ctx.message)
            await ctx.send(f"Owner: `{auth.display_name}`")
        else:
            await reactX(ctx)
            await ctx.send(
                f"Trigger for `{trigger}` not found.")

    @commands.command(aliases=["untrig"])
    @commands.guild_only()
    async def removetrigger(self, ctx: commands.Context,
                            trigger: str):
        '''
        Removes a message trigger if you're the owner
        '''
        if t := collection("triggers").find_one(
                {"server": ctx.guild.id, "trigger": trigger}):
            # Ensure no dupes in a single server
            auth = ctx.guild.get_member(t["user"])

            if auth == ctx.author:

                collection("triggers").delete_one(
                    {"server": ctx.guild.id, "trigger": trigger})
                await reactOK(ctx)
            else:
                await reactX(ctx)
                await ctx.send("You do not own this trigger.")
        else:
            await reactX(ctx)
            await ctx.send(
                f"Trigger for `{trigger}` not found.")

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if not message.author.bot and message.guild:
            await process_triggers(message)

            # Fun features
            if "@someone" in message.content.lower():
                e = discord.Embed(
                    description=random_member_from_server(message.guild.id, True).mention)
                e.set_footer(
                    text=f"Random ping by: {message.author.display_name}")
                await message.channel.send(embed=e)

            if not isNotThreat(2)(
                await self.bot.get_context(message)) and (len(
                    message.attachments) + len(
                    message.embeds) > 0 or is_url(message.content)):

                e = discord.Embed(title="You just posted cringe")
                e.set_image(
                    url=
                    "https://cdn.discordapp.com/attachments/419214713755402262/709165272447057981/unknown-11.png"
                )
                await message.channel.send(embed=e)

            # TODO: Re-add meme review in some capacity
