import discord
from discord.ext import commands

import math
import random
import requests

from db import collection

ACTIVE_SERVER = 419214713252216848
PNG_CHANNEL_ID = 522428899184082945

# depreciated
'''
class PNGS(commands.Cog):

    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.last_image = None
        self.last_tags = None
        self.last_number = None
        self.last_post = None

    @commands.command()
    @commands.is_nsfw()
    async def claimpng(self, ctx: commands.Context, *tags):
        # Claim a png
        claim = True
        user = ctx.author
        if self.last_number and len(tags) >= self.last_number:
            for i in tags:
                if i not in self.last_tags:
                    claim = False
            if claim:
                await ctx.send("Congratulations, you've claimed the last png!")



                collection("pngnsfw").insert_one({"imageID": self.last_post[0]['id'],
                          "server": ctx.guild.id,
                          "user": ctx.author.id,
                          "URL": self.last_post[0]['file_url'],
                          "claim_tags": tags,
                          "number": len(DBfind(PNG_COL,
                                               {"server": ctx.guild.id,
                                                "user": user.id}))})

                self.last_post = None
                self.last_number = None
                self.last_tags = None
            else:
                await ctx.send("You've got the tags wrong son, try again.")
        else:
            await ctx.send("You're gonna need more tags there son.")

    @commands.command()
    @commands.is_nsfw()
    async def listpngs(self, ctx: commands.Context, num: int = 1):
        # List your pngs
        user = ctx.author
        pages = math.ceil(
            len(DBfind(PNG_COL, {"server": ctx.guild.id, "user": user.id})) / 10)
        if 0 < num <= pages:
            def construct(
                pngs): return f"{pngs['number']+1}. **[{pngs['imageID']}]({pngs['URL']})**\n"
            s = ""

            pngs = DBfind(PNG_COL, {"server": ctx.guild.id, "user": user.id})

            terms = ""

            for i in range(
                    len(pngs) - 10 * num + 1,
                    len(pngs) - 10 * num + 11):
                if 0 < i:
                    s = construct(pngs[i - 1])
                    terms = s + terms

            e = discord.Embed(
                title=f"Page {num} of {pages} for {user.display_name}'s PNGs in {ctx.guild}",
                description=terms)
            await ctx.send(embed=e)
        else:
            await ctx.send("Please enter a valid page number.")

    @commands.command()
    @commands.is_nsfw()
    async def viewpng(self, ctx: commands.Context, args: int = None):
        # View your pngs
        if 0 < args <= len(
            DBfind(
                PNG_COL, {
                "server": ctx.guild.id, "user": ctx.author.id})):
            post = requests.get(
                "https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id=" + str(
                    DBfind(
                        PNG_COL, {
                            "server": ctx.guild.id, "user": ctx.author.id, "number": (
                                args - 1)})[0]['imageID'])).json()
            score = post[0]['score']
            postid = post[0]['id']
            tag_string = post[0]['tags']
            e = discord.Embed(
                title=str(args), description='ID: {postid}'.format(
                    postid=postid), url=DBfind(
                    PNG_COL, {
                        "server": ctx.guild.id, "user": ctx.author.id, "number": (
                            args - 1)})[0]['URL'], color=0xfecbed)
            e.set_author(name='Retrieved from Gelbooru')
            e.add_field(name='score',
                        value=post[0]['score'],
                        inline=True)
            e.add_field(name='rating',
                        value=post[0]['rating'],
                        inline=True)
            e.set_footer(text=tag_string)
            e.set_image(
                url=DBfind(
                    PNG_COL, {
                        "server": ctx.guild.id, "user": ctx.author.id, "number": (
                            args - 1)})[0]['URL'])
            await ctx.send(embed=e)
        else:
            await ctx.send("Please enter a valid PNG number.")


    async def spawn_png(self, message):
        url_base = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1'
        url_base = url_base + '&tags=-webm+sort%3arandom+'
        post = requests.get(url_base).json()
        self.last_post = post
        img_url = post[0]['file_url']
        self.last_tags = post[0]['tags']
        self.last_number = int(len(post[0]['tags']) / 200 + 3)
        e = discord.Embed(
            description=f":camera_with_flash: **A PNG HAS SPAWNED, NAME {self.last_number} OF ITS TAGS TO CLAIM IT**",
            color=0xfecbed)
        e.set_image(url=img_url)
        list1 = []
        tags = self.last_tags.split()
        for i in range(len(tags)):
            cuts = random.sample(
                range(len(tags[i])), int(len(tags[i]) / 2))
            cuttag = ""
            for j in range(len(tags[i])):
                if j in cuts:
                    cuttag += "_"
                else:
                    cuttag += tags[i][j]
            list1.append(cuttag)
        e.set_footer(text=" ".join(list1))


        channel_id = collection(
            "servers").find_one(message.guild.id)["channels"]["pngs"]
        pngchn = message.guild.get_channel(channel_id)
        await pngchn.send(embed=e)

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if random.randint(1, 100) < 5 and not message.author.bot:
            await self.spawn_png(message)
'''