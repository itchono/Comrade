# Method of requesting files from a user
from dis_snek.models.context import InteractionContext
from dis_snek.models.discord_objects.message import Attachment
from dis_snek.models.events import MessageCreate
import asyncio

import aiohttp

from io import BytesIO


async def request_file(ctx: InteractionContext,
                       prompt: str = None) -> Attachment:
    '''
    Sends a prompt to request a file from the author;
    will use up the response on the ctx object, so be careful
    '''
    if not prompt:
        prompt = "**FILE UPLOAD REQUEST**\n" \
            f"{ctx.author.mention}, "\
            "please send a file within the next 30 seconds."

    prompt_msg = await ctx.send(prompt)

    def message_check(event: MessageCreate):
        # Check that the message is from the author and has a file
        return event.message.author == ctx.author and event.message.attachments

    try:
        event: MessageCreate = await ctx.bot.wait_for(
            "message_create", timeout=30, checks=message_check)
    except asyncio.TimeoutError:
        await prompt_msg.edit(content="Upload request timed out.")
    else:
        # Get the first attachment
        attachment: Attachment = event.message.attachments[0]

        await ctx.channel.send("The content type of your file is "
                               f"{attachment.content_type} "
                               f"and has size {attachment.size} bytes.")
        return attachment


async def request_file_bytes(ctx: InteractionContext,
                             prompt: str = None) -> BytesIO:
    '''
    Returns a BytesIO object with the contents of the file
    '''
    attachment: Attachment = await request_file(ctx, prompt)

    # Bit stream for temporarily saving the attachment
    file_bytes = BytesIO()
    file_url = attachment.url

    # Download the contents of file_url onto file_bytes
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            file_bytes.write(await resp.read())
    file_bytes.seek(0)
    return file_bytes
