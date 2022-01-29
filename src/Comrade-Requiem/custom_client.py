from dataclasses import dataclass
from dis_snek.client import Snake
from pymongo.database import Database
from dis_snek.models.snek import (Context, Scale,
                                  InteractionContext, MessageContext)

from logger import log
from collections import defaultdict
from datetime import datetime


class CustomSnake(Snake):
    
    db: Database = None
    audit_log = defaultdict(list)
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

@dataclass
class CommandExecInfo:
    command_name: str
    kwargs: dict
    author_id: int
    time: datetime
# Stores command execution info for audit log


class CustomScale(Scale):
    def __init__(self, client: CustomSnake):
        self.client = client
        #self.add_scale_check(self.a_check)
        self.add_scale_postrun(self.post_run)
        
    # async def a_check(ctx: InteractionContext) -> bool:
    #     return bool(ctx.author.name.startswith("a"))

    async def post_run(self, ctx: InteractionContext):
        if ctx.guild_id:
            self.client.audit_log[ctx.guild_id].append(
                CommandExecInfo(
                    "idk",
                    ctx.kwargs,
                    ctx.author.id,
                    datetime.now()
                )
            )
        
