from utils.core_dependencies.utilities import *
from utils.core_dependencies.db_utils import *
from PIL import Image

## Shoujo Commands
## Full credit to Maggie Wang


with open('sparkles.txt', 'r', encoding="utf-8") as sparklesFile:
        sparkles = [s.strip() for s in sparklesFile.readlines()]

class Shoujo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def shoujosend(self, ctx, content):

        if not DBfind_one(CUSTOMUSER_COL,{"server":ctx.guild.id, "name":"ShoujoBot"}):
            us = self.bot.get_cog("Users")
            await us.addCustomUser(ctx, "ShoujoBot", avatar="https://cdn.discordapp.com/attachments/420664953435979806/749064831935447071/Annotation_2020-08-24_174359.jpg")

        c = self.bot.get_cog("Echo")
        await c.extecho(ctx, content, "ShoujoBot", deleteMsg=False)


    @commands.command()
    async def secret(self, ctx:commands.Context):
        '''
        sends all your deepest, darkest secrets into a black hole
        '''
        message = ctx.message
        try: await message.delete()
        except: pass

        await self.shoujosend(ctx, "Don't worry, your secret is safe with me~ (^_<)〜☆")

    @commands.command()
    async def sparklify(self, ctx:commands.Context, *, message=None):
        '''
        makes your message extra kawaii desu~
        '''
        if message:
            sparkle = random.choice(sparkles)

            sparklyMessage = f"`{sparkle} {message} {sparkle[-1::-1]}`"

            try: await ctx.message.delete()
            except: pass

            await self.shoujosend(ctx, sparklyMessage)
        else:
            url = ctx.message.attachments[0].url
            #size = (ctx.message.attachments[0].width, ctx.message.attachments[0].height)
            with open('source.png', 'wb') as f:
                await ctx.message.attachments[0].save(f)

            ogImage = Image.open('source.png')
            size = ogImage.size

            sparkle_image = Image.open("sparkle.png")#.resize(size)
            ratio = sparkle_image.size[0]/sparkle_image.size[1] #width/height
            sparkle_image = sparkle_image.resize((size[0], int(size[0]/ratio)))
            
            ogImage.paste(sparkle_image, (0,0), sparkle_image)
            ogImage.save('sparklified.png', "PNG")

            with open('sparklified.png', 'rb') as f:
                await ctx.send(file = discord.File(f, 'sparklified.png'))
            os.remove('sparklified.png')
            os.remove('source.png')

    @commands.command()
    @commands.check(isOP)
    async def addSparkle(self, ctx:commands.Context, *, sparkle):
        '''
        share the kawaii love ~
        '''
        with open('sparkles.txt', 'a') as file:
            file.write(sparkle)