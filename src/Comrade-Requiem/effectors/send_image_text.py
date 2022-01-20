from dis_snek.models.context import InteractionContext

from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from dis_snek.models.file import File

import textwrap

async def send_amongus(ctx: InteractionContext, text: str):
    '''
    Sends a message as among us font in image form
    '''
    await ctx.defer(ephemeral=True)
    
    # Import font
    font = ImageFont.truetype("static/AmongUs-Regular.ttf", size=50)
    
    # Remove all non alphabetical or spacecharacters from the text, capitalize
    text = "".join(char.upper()
                   for char in text if char.isalpha() or char == " ")
    
    # Wrap text so that each line is no longer than 30 characters
    text = textwrap.wrap(text, 30)
    
    # Determine dimensions of the text
    text_width, text_height = font.getsize(max(text, key=len))
    
    # Multiply by the number of lines
    text_height *= len(text)
    text = "\n".join(text)
    
    # Create new transparent image with the correct size
    image = Image.new("RGBA", (text_width, text_height), (0, 0, 0, 0))
    
    # Draw text onto the image
    draw = ImageDraw.Draw(image)
    draw.multiline_text((0, 0), text, font=font, fill=(255, 255, 255, 255))
    
    file_bytes = BytesIO()
    image.save(file_bytes, "PNG")
    file_bytes.seek(0)
    
    send_file = File(file_bytes, file_name="amongus.png")
    
    await ctx.channel.send(file=send_file)
    # Send the image to the channel
    await ctx.send("AMOGUS", ephemeral=True)