from __future__ import unicode_literals
from utils.utilities import *
from utils.mongo_interface import *

from pybooru import Danbooru


class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def hentai(self, ctx:commands.Context, tags:str="", num:int = 1):
        '''
        Fetches a number of posts from Danbooru given a series of tags. Input with quotes.
        Ex. $c hentai "arms_up solo" 2

        User $c hentai clear to purge all hentai messages
        '''
        if tags.lower() == "clear":
            global purgeTGT
            purgeTGT = self.bot.user
            await ctx.channel.purge(check=purgeCheck, bulk=True)
            purgeTGT = None
        elif num > 20:
            await ctx.send("Are you fucking serious")
        else:
            if ctx.channel.id == getCFG(ctx.guild.id)["hentai channel"]:
                client = Danbooru('danbooru')
                
                posts = client.post_list(tags=tags, limit=num, random=True)

                if not posts:
                    await ctx.send("No results found. Please try another tag.")
                else:
                    for post in posts:
                        try:
                            e = discord.Embed(title=tags, url=post["file_url"])
                            e.set_image(url=post["file_url"])
                            await ctx.send(embed=e)
                        except:
                            e = discord.Embed(title=tags, description="Unknown Image Format, Could not be embedded.")
            else:
                await delSend("Please use this command in the hentai channel.", ctx.channel)