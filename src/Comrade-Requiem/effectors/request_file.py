# Method of requesting files from a user
from dis_snek.models.snek import (InteractionContext, slash_option, OptionTypes)
from dis_snek.models.discord import Attachment
from dis_snek.api.events import MessageCreate
import asyncio
from imghdr import what
import aiohttp
from io import BytesIO
from logger import log
from processors.tenor_converter import get_tenor_gif


async def request_file(ctx: InteractionContext,
                       prompt: str = None,
                       timeout: int = 30) -> Attachment:
    '''
    Sends a prompt to request a file from the author and returns the file.
    '''
    if not prompt:
        prompt = "**FILE UPLOAD REQUEST**\n" \
            f"{ctx.author.mention}, "\
            "please send a file within the next 30 seconds."

    prompt_msg = await ctx.send(prompt)

    def message_check(event: MessageCreate):
        # Check that the message is from the author and has a file
        if event.message._guild_id:
            return event.message.author == ctx.author \
                and event.message.attachments \
                and event.message.channel == ctx.channel
        else:
            return event.message.author == ctx.author and event.message.attachments

    try:
        event: MessageCreate = await ctx.bot.wait_for(
            "message_create", timeout=timeout, checks=message_check)
    except asyncio.TimeoutError:
        await prompt_msg.edit(content="Upload request timed out.")
    else:
        # Get the first attachment
        attachment: Attachment = event.message.attachments[0]
        
        log.info("File requested and received: "
                    f"{attachment.content_type}:"
                    f" {attachment.size} bytes.")
        return attachment


async def request_file_bytes(ctx: InteractionContext,
                             prompt: str = None,
                             timeout: int = 30) -> BytesIO:
    '''
    Returns a BytesIO object with the contents of the file
    '''
    return await attachment_to_bytes(await request_file(ctx, prompt, timeout))


async def attachment_to_bytes(attachment: Attachment) -> BytesIO:
    '''
    Returns a BytesIO object with the contents of the attachment
    '''
    # Bit stream for temporarily saving the attachment
    file_bytes = BytesIO()
    file_url = attachment.url

    # Download the contents of file_url onto file_bytes
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as resp:
            file_bytes.write(await resp.read())
    file_bytes.seek(0)
    return file_bytes

class ImageBytes():
    @classmethod
    async def convert(cls, ctx: InteractionContext, url: str):
        # Downloads the image at url and returns a BytesIO object
        
        if not ctx.responded:
            await ctx.defer()
            # Defer execution because downloading will take time

        if url.startswith("https://tenor.com/view/"):
            url = await get_tenor_gif(url)
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                file_bytes = BytesIO()
                file_bytes.write(await resp.read())
                file_bytes.seek(0)
                
                # Assert that the image is valid
                if not what(file_bytes):
                    raise ValueError(
                        "The image at the URL you provided is not valid.")
                return file_bytes


def image_url(required: bool = False):
    """Call with `@my_own_int_option()`"""

    def wrapper(func):
        return slash_option(
            name="image_url",
            description="URL linking to the image",
            opt_type=OptionTypes.STRING,
            required=required
        )(func)

    return wrapper

