from dataclasses import dataclass
from dis_snek.client import Snake
from pymongo.database import Database
from dis_snek.models.snek import (Context,
                                  InteractionContext,
                                  MessageContext)
from dis_snek.models.discord import Guild, GuildText
import logging
from collections import defaultdict, deque
from datetime import datetime


log = logging.getLogger("ComradeLog")

class CustomSnake(Snake):
    db: Database = None
    audit_log = defaultdict(lambda: defaultdict(lambda: deque(maxlen=10)))
    relay_guild: Guild = None
    relay_channel: GuildText = None
    emote_channels: dict = {}
    
    async def on_command_error(self, ctx: Context,
                               error: Exception):
        log.exception(msg=error, exc_info=error)
        if type(ctx) == InteractionContext and not ctx.responded:
            await ctx.send("Something went wrong while executing the command.\n"
                           f"Error: `{error}`", ephemeral=True)
        elif type(ctx) == MessageContext:
            await ctx.send("Something went wrong while executing the command.\n"
                           f"Error: `{error}`", reply_to = ctx.message)        
            
    async def on_error(self, source: str, error: Exception, *args, **kwargs) -> None:
        log.exception(msg=error, exc_info=error)
        await super().on_error(source, error, *args, **kwargs)
        
        
    async def on_command(self, ctx: Context) -> None:
        # log command execution
        if ctx.guild_id and ctx.channel:
            self.audit_log[ctx.guild_id][ctx.channel.id].append(
                CommandExecInfo(
                    ctx.invoked_name,
                    ctx.args,
                    ctx.kwargs,
                    ctx.author.id,
                    datetime.now()
                )
            )
        await super().on_command(ctx)


@dataclass
class CommandExecInfo:
    command_name: str
    args: list
    kwargs: dict
    author_id: int
    time: datetime
# Stores command execution info for audit log
