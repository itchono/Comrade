from dis_snek.models.scale import Scale
from dis_snek.models.application_commands import slash_command
from dis_snek.models.context import InteractionContext
from logger import logger

from dis_snek.models.discord_objects.message import Attachment
from dis_snek.models.file import File

from effectors.request_file import request_file_bytes
from PIL import Image


class ImageModification(Scale):
    @slash_command(name="zamn",
                   description="ZAMN!! Edits an image to ZAMN it.",
                   scopes=[419214713252216848, 709954286376976425])
    async def zamn(self, ctx: InteractionContext):

        file_bytes: Attachment = await request_file_bytes(
            ctx,
            "**FILE UPLOAD REQUEST**\n"
            f"{ctx.author.mention}, "
            "please upload an image within the next 30 seconds.")

        # Load the image from file_bytes
        ogImage = Image.open(file_bytes)
        template = Image.open("static/zamn.png")
        ratio = ogImage.size[0]/ogImage.size[1]
        ogImage = ogImage.resize((int(360 * ratio), 360))

        # Paste the image onto the template
        template.paste(ogImage, (254-int((ogImage.size[0]-249)/2), 73))
        template2 = Image.open("static/zamn.png")
        template.paste(template2, (0, 0), template2)
        file_bytes.seek(0)
        template.save(file_bytes, "PNG")
        file_bytes.seek(0)

        send_file = File(file_bytes, file_name="zamn.png")

        await ctx.channel.send(file=send_file)
        # Send the image to the channel


def setup(bot):
    ImageModification(bot)
    logger.info("Module image_modification.py loaded.")
    