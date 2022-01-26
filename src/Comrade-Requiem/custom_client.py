from dis_snek.client import Snake
from pymongo.database import Database
from dis_snek.models.snek import (Context,
                                  InteractionContext, MessageContext)

from logger import log


class CustomSnake(Snake):
    
    db: Database = None
    audit_log = {}
    # TODO: log command execution
    
    async def on_command_error(self, ctx: Context,
                               error: Exception):
        log.exception(msg=error, exc_info=error)
        if type(ctx) == InteractionContext and not ctx.responded:
            await ctx.send("Something went wrong while executing the command.\n"
                           f"Error: `{error}`", ephemeral=True)
        elif type(ctx) == MessageContext:
            await ctx.send("Something went wrong while executing the command.\n"
                           f"Error: `{error}`", reply_to = ctx.message)        
