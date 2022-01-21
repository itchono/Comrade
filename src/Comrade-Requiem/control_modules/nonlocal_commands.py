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


def fake_ctx(ctx: Context) -> InteractionContext:
    
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
    
    return new_ctx


async def execute_slash_command(ctx: Context, command: str, *args):
    '''
    Executes any slash command registered with the bot.
    '''

    bot: Snake = ctx.bot
    
    command: SlashCommand
    if command := bot.interactions[ctx.guild_id][command]:
        # log.info(f"Executing slash command {command.name}"
        #          f" with function signature {signature(command.callback)}")
                
        await command.callback(fake_ctx(ctx), *args)
        
    else:
        raise ValueError(f"Command {command} not found.")
    
class NonlocalCommands(Scale):
    @message_command()
    async def runcommand(self, ctx: MessageContext, command: str, *args):
        '''
        Executes any slash command registered with the bot.
        '''
        await execute_slash_command(ctx, command, *args)
    
    
def setup(bot):
    NonlocalCommands(bot)
    log.info("Module nonlocal_commands.py loaded.")
    