import re
from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import slash_command, SlashCommandOption, OptionTypes
from dis_snek.models.context import InteractionContext
from dis_snek.models.discord_objects.user import Member

from effectors.echo_webhook import echo

class MiscFun(Scale):
    @slash_command(name="echo", description="echoes a message as another person", scopes=[419214713252216848, 709954286376976425],
                   options=[SlashCommandOption(
                       name="message",
                       type=OptionTypes.STRING,
                       description="the message to echo",
                       required=True
                        ),
                        SlashCommandOption(
                       name="author",
                       type=OptionTypes.USER,
                       description="user to impersonate",
                       required=False
                   )])
    async def echo_command(self, ctx: InteractionContext, message: str, author: Member=None):
        if not author:
            author = ctx.author
        await echo(ctx, author, message)

def setup(bot):
    MiscFun(bot)
    print("Module misc_fun.py loaded.")
