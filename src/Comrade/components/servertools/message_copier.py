# Message Copier; Unchanged from 4.0
import discord
from discord.ext import commands
import asyncio
from utils.checks import isServerOwner


class Copier(commands.Cog):
    '''
    Copies messages from one channel to another channel
    '''

    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.check_any(commands.is_owner(), isServerOwner())
    async def copymessages(self, ctx: commands.Context,
                           source: discord.TextChannel,
                           destination: discord.TextChannel):
        '''
        Exports channel texts to another channel
        '''
        await ctx.send(f"{ctx.author.mention}, you are about to start a transfer from {source.mention} to {destination.mention}. **THIS IS A POTENTIALLY DESTRUCTIVE ACTION**. Please type `confirm` with the next 60 seconds to continue.")

        def check(m):
            return m.content == 'confirm' and m.channel == ctx.channel and m.author == ctx.author

        try:
            await self.bot.wait_for('message', timeout=60.0, check=check)

            await ctx.send(f"Transfer from {source.mention} to {destination.mention} is in progress. This will take several minutes depending on the size of the channel.")

            webhook = None
            for wh in await destination.webhooks():
                if wh.name == "ChannelCopier":
                    webhook = wh
            if not webhook:
                webhook = await destination.create_webhook(name="ChannelCopier", avatar=None)

            async for message in source.history(limit=None, oldest_first=True):
                m = await webhook.send(wait=True, content=message.content, username=message.author.display_name, avatar_url=message.author.avatar_url, embeds=message.embeds, files=[await a.to_file() for a in message.attachments])
                for r in message.reactions:
                    await m.add_reaction(r)

        except asyncio.TimeoutError:
            await ctx.send("Tranfer aborted.")
        else:
            await ctx.send(
                f"Transfer from {source.mention} to {destination.mention} completed successfully.")
