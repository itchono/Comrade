from dis_snek.models.snek import InteractionContext
from dis_snek.models.discord import Attachment
from dis_snek.api.events import MessageCreate
import asyncio


async def request_macro_input(ctx: InteractionContext,
                       prompt: str = None,
                       timeout: int = 300) -> str:
    '''
    Sends a prompt to request a macro input from the author
    '''
    if not prompt:
        prompt = "**TEXT INPUT REQUEST**\n" \
            f"{ctx.author.mention}, "\
            "please type out and send your macro within the next 5 minutes."

    prompt_msg = await ctx.channel.send(prompt)

    def message_check(event: MessageCreate):
        # Check that the message is from the author and has a file
        if event.message._guild_id:
            return event.message.author == ctx.author \
                and event.message.channel == ctx.channel
        else:
            return event.message.author == ctx.author

    try:
        event: MessageCreate = await ctx.bot.wait_for(
            "message_create", timeout=timeout, checks=message_check)
    except asyncio.TimeoutError:
        await prompt_msg.edit(content="Upload request timed out.")
    else:
        text = event.message.content.strip("```").strip("\n")
        return text
