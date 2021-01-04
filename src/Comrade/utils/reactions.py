from discord.ext import commands


async def reactOK(ctx: commands.Context):
    '''
    Adds reaction to show that task was completed successfully.
    '''
    await ctx.message.add_reaction("👍")


async def reactX(ctx: commands.Context):
    '''
    Adds reaction to show that task was forbidden.
    '''
    await ctx.message.add_reaction("❌")


async def reactQuestion(ctx: commands.Context):
    '''
    Adds reaction to show that something went wrong
    '''
    await ctx.message.add_reaction("❓")
