import discord
from discord.ext import commands
from utils import *

from PIL import Image
import os, random, requests

## Shoujo Commands
## Credit to Maggie Wang

with open('sparkles.txt', 'r', encoding="utf-8") as sparklesFile:
    sparkles = [s.strip() for s in sparklesFile.readlines()]

with open('yukis_feelings.txt', 'r', encoding="utf-8") as kimochiFile:
    kimochi = [s.split('\n') for s in kimochiFile.read().split('%')][1:] #change text so first section does not start with %, remove indexing
    # TL Note: kimochi means feeling, but in Japanese

thoughts = {}
for action in kimochi:
    thoughts[action[0]] = action[1:]

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
        feelings = random.choice(thoughts['sparklify'])
        if '{}' in feelings:
            friend = ctx.message.author.display_name

            shoujo_role_exists = 'Shoujotard' in [r.name for r in ctx.guild.roles]
            author_has_shoujo_role = shoujo_role_exists and 'Shoujotard' in [r.name for r in ctx.author.roles]

            ## in the case that the Shoujotard role doesn't exist, call everyone chan
            ## Else, only call those who have the Shoujotard role chan
            if (author_has_shoujo_role or not shoujo_role_exists): friend += '-chan'
            feelings = feelings.replace('{}', friend)

        if message:
            sparkle = random.choice(sparkles)

            sparklyMessage = f"`{sparkle} {message} {sparkle[-1::-1]}`"

            try: await ctx.message.delete()
            except: pass
            await ctx.send(sparklyMessage)
        
        else:
            await ctx.trigger_typing()
            url = ctx.message.attachments[0].url
            with open('source.png', 'wb') as f:
                await ctx.message.attachments[0].save(f)

            ogImage = Image.open('source.png')
            size = max(ogImage.size)

            kiraKira = Image.open("sparkle.png").resize((size,size))
            ogImage.paste(kiraKira, (0,0), kiraKira)
            ogImage.save('sparklified.png', "PNG")

            with open('sparklified.png', 'rb') as f:
                await ctx.send(feelings, file = discord.File(f, 'sparklified.png'))
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