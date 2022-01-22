# Execute commands without needing to go through slash routes
from dis_snek.models.context import Context, InteractionContext, MessageContext
from dis_snek.models.scale import Scale
from dis_snek import Snake
from dis_snek.models.application_commands import SlashCommand
from dis_snek.models.command import message_command
from dis_snek.utils import find
from inspect import signature
from logger import log
from copy import copy


def fake_ctx(ctx: Context, args) -> InteractionContext:
    
    new_ctx = copy(ctx)
    
    # an imposter ctx class that can be initialized
    # using a generic Context and treated as an InteractionContext
    # this is a workaround for the fact that the InteractionContext
    # sometimes will be deferred.
    new_ctx.deferred = True
    new_ctx.responded = True
    new_ctx.ephemeral = False

    async def defer(ephemeral=False) -> None:
        """
        Dummy function to make the InteractionContext
        behave as an InteractionContext
        """
        pass
    
    new_ctx.defer = defer
    
    # Pass in args to the function
    new_ctx.args = args
    
    return new_ctx


async def execute_slash_command(ctx: Context, cmd_name: str, args):
    '''
    Executes any slash command registered with the bot.
    '''
    if cmd_name in ctx.bot.interactions[ctx.guild_id]:
        command: SlashCommand = ctx.bot.interactions[ctx.guild_id][cmd_name]
        # log.info(f"Executing nonlocal command {command.name}"
        #          f" with function signature {signature(command.callback)}")
        await command.call_callback(command.callback, fake_ctx(ctx, list(args)))
    else:
        raise ValueError(f"Command {cmd_name} not found.")


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
    log.info("Module nonlocal_commands.py loaded.")
    