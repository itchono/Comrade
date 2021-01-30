from discord.ext import commands

from utils.echo import echo

from collections import defaultdict


class Sniper(commands.Cog):
    '''
    Similar to Dank Memer Bot's snipe functionality
    '''
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.last_deleted = defaultdict(lambda: None)
        self.last_edited = defaultdict(lambda: None)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.last_deleted[message.channel.id] = message

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        self.last_deleted[after.channel.id] = (before, after)

    @commands.command()
    async def deleted(self, ctx: commands.Context):
        '''
        Retrieves the last message deleted in the channel
        '''
        if msg := self.last_deleted[ctx.channel.id]:
            await echo(ctx, msg.author, msg.content,
                       msg.attachments[0] if msg.attachments else None,
                       msg.embeds[0] if msg.embeds else None)
            self.last_deleted[ctx.channel.id] = None
        else:
            await ctx.send("No known deleted messages")

    @commands.command()
    async def edited(self, ctx: commands.Context):
        '''
        Retrieves the last message edited in the channel
        '''
        if msg := self.last_edited[ctx.channel.id]:
            before, after = msg
            await echo(ctx, before.author, before.content,
                       before.attachments[0] if before.attachments else None,
                       before.embeds[0] if before.embeds else None)
            await ctx.send(after.jump_url)
            self.last_edited[ctx.channel.id] = None
        else:
            await ctx.send("No known edited messages")
