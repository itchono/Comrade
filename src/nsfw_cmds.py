from __future__ import unicode_literals
from utils.utilities import *
from utils.mongo_interface import *

from pybooru import Danbooru


class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def hentai(self, ctx, tags:str):
        print("working...")

        if ctx.channel.id == getCFG(ctx.guild.id)["hentai channel"]:
            client = Danbooru('danbooru')
            
            posts = client.post_list(tags='blue_eyes', limit=5)

            for post in posts:
                print("Image path: {0}".format(post['file_url']))