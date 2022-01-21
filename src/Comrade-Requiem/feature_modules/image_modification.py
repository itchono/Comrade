from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import slash_command
from dis_snek.models.context import InteractionContext
from logger import log

from dis_snek.models.file import File

from PIL import Image
from effectors.request_file import request_file_bytes, ImageBytes, image_url
from io import BytesIO


class ImageModification(Scale):
    @slash_command(name="zamn",
                   description="ZAMN!! Upload an image to ZAMN it.",
                   scopes=[419214713252216848, 709954286376976425])
    @image_url()
    async def zamn(self, ctx: InteractionContext, file_bytes: ImageBytes = None):
        if not file_bytes:
            file_bytes: BytesIO = await request_file_bytes(
                ctx,
                "**FILE UPLOAD REQUEST**\n"
                f"{ctx.author.mention}, "
                "please upload an image within the next 30 seconds.")

        # Load the image from file_bytes
        user_image = Image.open(file_bytes)
        meme_template = Image.open("static/zamn.png")
        
        # Create a blank image with the same size as the template
        meme = Image.new("RGBA", meme_template.size)
        
        ratio = user_image.size[0]/user_image.size[1]
        user_image = user_image.resize((int(360 * ratio), 360))

        # Paste the image onto the template
        meme.paste(user_image, (254-int((user_image.size[0]-249)/2), 73))
        meme.paste(meme_template, (0, 0), mask=meme_template)
        file_bytes.seek(0)
        meme.save(file_bytes, "PNG")
        file_bytes.seek(0)

        send_file = File(file_bytes, file_name="zamn.png")

        await ctx.channel.send(file=send_file)
        # Send the image to the channel
        
        if not ctx.responded:
            await ctx.send("ZAMN'd!")


def setup(bot):
    ImageModification(bot)
    log.info("Module image_modification.py loaded.")
    