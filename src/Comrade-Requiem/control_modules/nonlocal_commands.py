# Execute commands without needing to go through slash routes
from dis_snek.models.context import MessageContext
from dis_snek.models.scale import Scale
from dis_snek.models.command import message_command
from inspect import signature
from logger import log

from effectors.nonlocal_executor import execute_slash_command


class NonlocalCommands(Scale):
    @message_command()
    async def runcommand(self, ctx: MessageContext, command: str, *args):
        '''
        Executes any slash command registered with the bot.
        '''
        await execute_slash_command(ctx, command, args)

    @message_command()
    async def inspect(self, ctx: MessageContext, command: str):
        '''
        Inspects the function signature of a registered slash command.
        '''
        if cmd := ctx.bot.interactions[ctx.guild_id][command]:
            await ctx.send(f"{command} has signature {signature(cmd.callback)}")
        else:
            await ctx.send(f"Command {command} not found.")
    
def setup(bot):
    NonlocalCommands(bot)
    log.info("Module execute_nonlocal_commands.py loaded.")
