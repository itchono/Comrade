from __future__ import unicode_literals
from utils.utilities import *
from utils.mongo_interface import *

import requests
import json
import string
import io
import aiohttp

class NSFW(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def hentai(self, ctx:commands.Context, *args):
        '''
        Fetches a number of posts from Danbooru given a series of tags.
        Ex. $c hentai arms_up solo 2

        User $c hentai clear to purge all hentai messages
        '''
        limit = 1
        tag_list = []
        if len(args) > 0:
            if args[len(args) - 1].isnumeric():
                limit = int(args[len(args) - 1])
                for i in range(len(args) - 1):
                    tag_list.append(args[i])
            else:
                for i in range(len(args)):
                    tag_list.append(args[i])

        if limit > 20:
            await ctx.send("Can you calm your genitals")
        else:
            if ctx.channel.id == getCFG(ctx.guild.id)["hentai channel"]:
                if "clear" in tag_list:
                    setTGT(self.bot.user)
                    await ctx.channel.purge(check=purgeCheck, bulk=True)
                else:
                    url_base = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1'
                    url_base = url_base + '&limit={limit}&tags=-rating%3asafe+sort:random+'.format(limit=limit)
                    for i in range(len(tag_list)):
                        url_base = url_base + '{tag}+'.format(tag=tag_list[i])
                        
                    print(url_base)
                    try:
                        posts = requests.get(url_base).json()
                    except ValueError:
                        await ctx.send("No results found. Please try another tag.")
                        return
                    
                    if len(tag_list) == 0:
                        count = "N/A"
                    else:
                        new_tag = tag_list[0]
                        if tag_list[0].endswith('*'):
                            new_tag = tag_list[0][:len(tag_list[0])-1]
                        try:
                            num_results = requests.get('https://gelbooru.com/index.php?page=dapi&s=tag&q=index&json=1&name={tags}'.format(tags=new_tag)).json()
                        except:
                            count = "N/A"
                        else:
                            if len(num_results) != 0:
                                count = num_results[0]['count']
                            else:
                                count = 0
                    for i in range(len(posts)):
                        img_url = posts[i]['file_url']

                        score = posts[i]['score']
                        postid = posts[i]['id']
                        tags = ""
                        for k in range(len(tag_list)):
                            tags += " " + tag_list[k] 
                        tag_string = posts[i]['tags']
                        e = discord.Embed(title=tags, description ='ID: {postid}'.format(postid=postid), url=img_url, color=0xfecbed)
                        e.set_author(name='Retrieved from Gelbooru')
                        e.add_field(name='score', value=posts[i]['score'], inline=True)
                        e.add_field(name='rating', value=posts[i]['rating'], inline=True)
                        e.add_field(name='hit count', value=count, inline=True)
                        e.set_footer(text=tag_string)
                        e.set_image(url=img_url)

                        if img_url.endswith(".webm"):
                            async with aiohttp.ClientSession() as session:
                                async with session.get(img_url) as resp:
                                    if resp.status != 200:
                                        await channel.send('Could not download file.')
                                    else:
                                        data = io.BytesIO(await resp.read())
                                        e.set_thumbnail(url='https://img.icons8.com/cotton/2x/movie-beginning.png')
                                        await ctx.send(embed=e)
                                        await ctx.send(file=discord.File(data, img_url))
                        else:
                            e.set_thumbnail(url='https://vectorified.com/images/image-gallery-icon-21.png')
                            await ctx.send(embed=e)

            else:
                await delSend("Please use this command in the hentai channel.", ctx.channel)
