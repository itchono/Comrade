from dis_snek.models.snek import (Scale, slash_command,
                                  InteractionContext, slash_option,
                                  OptionTypes)
from dis_snek.models.discord import File
from logger import log

from PIL import Image, ImageDraw, ImageFont
from effectors.request_file import request_file_bytes, ImageBytes, image_url
from io import BytesIO
import textwrap


class ImageModification(Scale):
    @slash_command(name="zamn",
                   description="ZAMN!! Upload an image to ZAMN it.",
                   scopes=[419214713252216848, 709954286376976425])
    @image_url()
    async def zamn(self, ctx: InteractionContext, image_url: ImageBytes = None):
        if not image_url:
            file_bytes: BytesIO = await request_file_bytes(
                ctx,
                "**FILE UPLOAD REQUEST**\n"
                f"{ctx.author.mention}, "
                "please upload an image within the next 30 seconds.")
        else:
            file_bytes = image_url

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

        await ctx.send(file=send_file)
        # Send the image to the channel
        
        if not ctx.responded:
            await ctx.send("ZAMN'd!")
            
    @slash_command(name="the",
                   description="Make a Barnacle Boy \"the\" meme.",
                   scopes=[419214713252216848, 709954286376976425])
    @slash_option(name="caption", description="Caption for the meme",
                  opt_type=OptionTypes.STRING, required=True)
    @image_url()
    async def the(self, ctx: InteractionContext, caption: str, image_url: ImageBytes = None):
        if not ctx.deferred:
            await ctx.defer()

        # Load the image
        meme= Image.open("static/barnacleboy.png")
        
        file_bytes = BytesIO()
        font = ImageFont.truetype("static/impact.ttf", size=50)
        
        text = "".join(char.upper()
                    for char in caption if char.isalpha() or char == " ")
        text = textwrap.wrap(text, 30)
        text_width, text_height = font.getsize(max(text, key=len), stroke_width=2)
        text_height = int(text_height * 1.1) if len(text) > 1 else text_height
        
        # Multiply by the number of lines
        text_height *= len(text)
        text = "\n".join(text)
        
        # Create new transparent image with the correct size
        text_layer = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(text_layer)
        draw.multiline_text((0, 0), text, font=font, fill=(255, 255, 255, 255),
                            stroke_fill=(0, 0, 0, 255), stroke_width=2)
    
        # Resize the text layer so that width is within a 450 x 110 box
        if text_height/text_width > 110/450:
            text_layer = text_layer.resize((int(110*text_width/text_height), 110))
        else:
            text_layer = text_layer.resize((450, int(450*text_height/text_width)))
            
        # Paste the text layer onto the template at (210, 10)
        meme.paste(text_layer, (210, 10), mask=text_layer)
        
        # If the user image exists, resize it and paste it
        if image_url:
            user_image = Image.open(image_url).convert('RGBA')
            ratio = user_image.size[0]/user_image.size[1]
            if ratio < 1:
                user_image = user_image.resize((int(330 * ratio), 330))
                meme.paste(user_image, (20, 200), mask=user_image)
            else:
                user_image = user_image.resize((300, int(300 / ratio)))
                margin = (330 - user_image.size[1])
                meme.paste(user_image, (20, 200+margin), mask=user_image)
        
            

        meme.save(file_bytes, "PNG")
        file_bytes.seek(0)

        send_file = File(file_bytes, file_name="the.png")

        await ctx.send(file=send_file)
        # Send the image to the channel


def setup(bot):
    ImageModification(bot)
    log.info("Module image_modification.py loaded.")
    