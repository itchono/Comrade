from __future__ import unicode_literals
from utils.utilities import *
from utils.mongo_interface import *

from pybooru import Danbooru


class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def hentai(self, ctx:commands.Context, tags:str, num:int):
        print("working...")

        if ctx.channel.id == getCFG(ctx.guild.id)["hentai channel"]:
            client = Danbooru('danbooru')
            
            posts = client.post_list(tags=tags, limit=num)

            if not posts:
                await ctx.send("No results found. Please try another tag.")
            else:
                for post in posts:
                    e = discord.Embed(title=tags, url=post["file_url"])
                    e.set_image(url=post["file_url"])
                    print("sending...")
                    await ctx.send(embed=e)
        else:
            await delSend("Please use this command in the hentai channel.", ctx.channel)