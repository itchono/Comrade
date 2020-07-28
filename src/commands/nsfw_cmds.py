from __future__ import unicode_literals
from utils.utilities import *
from utils.mongo_interface import *

import json
import io
import aiohttp
import re
import urllib.request
from bs4 import BeautifulSoup
from random import randrange

class NSFW(commands.Cog):
    '''
    Hentai.
    Credits to Sunekku (Nuha Sahraoui).
    '''
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.last_search = ""
        self.cur_page = 0
        self.prev_search = None
        self.extensions = None
        self.prev_tag = ""

        self.last_image = None

    @commands.command()
    @commands.is_nsfw()
    async def nsearch(self, ctx: commands.Context, *, args:str = "small breasts"):
        '''
        Searches for a hentai on nhentai.net
        '''
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,}
        tags = re.split("\s", args)
        url = 'https://nhentai.net/search/?q='
        for i in range(len(tags)):
            url += (tags[i] + '+')
        request = urllib.request.Request(url,None,headers)
        try:
            response = urllib.request.urlopen(request)
        except ValueError:
            await ctx.send(
                "No results found. Please try another tag.")
            return
        
        data = response.read()
        soup = BeautifulSoup(data, 'html.parser')
        num_results = re.findall(r'(?<=/i> ).*?(?= r)', str(soup.h1))[0]
        num_results = re.split('\,', num_results)
        if 'No' in (num_results):
            await ctx.send(
                "No results found. Please try another tag.")
            return
        
        self.prev_tag = args

        num = ""
        for k in range(len(num_results)):
            num += num_results[k]
        num = int(num)
        if num % 25 != 0:
            num_pages = num//25 + 1
        else:
            num_pages = num//25
        page = randrange(1, num_pages + 1)
        url2 = url + '&page={page}'.format(page=page)
        request = urllib.request.Request(url2,None,headers)
        response = urllib.request.urlopen(request)
        data = response.read()
        soup = BeautifulSoup(data, 'html.parser')

        list_nums = []
        for j in range(len(soup.find_all('a'))):
            entry = soup.find_all('a')[j]
            thing = BeautifulSoup(str(entry))
        
            thing2 = thing.a['href']
            if re.search("^/g/\d+", thing2):
                search_number = int(re.findall(r"g/(\d+)/", thing2)[0])
                list_nums.append(search_number)

        search = list_nums[randrange(len(list_nums))]
    
        await self.nhentai(ctx = ctx, args = search)

    @commands.command()
    @commands.is_nsfw()
    async def nhentai(self, ctx: commands.Context, args:int = 185217):
        '''
        Fetches a hentai from nhentai.net, by ID.
        '''
        self.cur_page = 0
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,}
        url = 'https://nhentai.net/g/{num}/'.format(num=args)
        request = urllib.request.Request(url,None,headers)
        try:
            response = urllib.request.urlopen(request)
        except:
            await ctx.send(
                "No results found. Please try another entry.")
            return
        
        
        data = response.read()
        soup = BeautifulSoup(data, 'html.parser')
        thing = soup.find_all('meta')[3]
        thing = str(thing)
        title = soup.find_all('meta')[2]
        title = str(title)
        title = re.findall(r'(?<=").*?(?=")', title)[0]

        araragi_san = []

        wot = str(soup.find_all('section')[1])
        wot = BeautifulSoup(wot)
        hi = wot.find_all('a')
        for k in range(len(hi)):
            penis_birth = hi[k]
            nipple_birth = BeautifulSoup(str(penis_birth))
            ntr = nipple_birth.a['href']
            if re.search('/artist/', ntr):
                araragi_san = re.findall(r'(?<=/).*?(?=/)', ntr)
        
        gallerynumber = int(re.findall(r"galleries/(\d+)/cover.", thing)[0])

        imgs = []
        for i in range(len(soup.find_all('noscript'))):
            s = soup.find_all('noscript')[i]
            s = str(s)
            new_soup = BeautifulSoup(s)
            x = new_soup.img['src']
            if re.search('/{}/'.format(gallerynumber), s):
                y = re.split("\.", x)
            imgs.append(y[len(y) - 1])
        self.extensions = imgs

        if araragi_san:
            araragi_san.pop(0)
            value = araragi_san[0]
        else:
            value = "N/A"

        
        img_url = 'https://t.nhentai.net/galleries/{gallerynumber}/cover.'.format(gallerynumber = gallerynumber) + imgs[0]
        self.last_image = img_url
        e = discord.Embed(
                            title=title,
                            description='ID: {postid}'.format(postid=args),
                            url=url,
                            color=0xfecbed)
        e.add_field(name='artist',
                                    value=value,
                                    inline=True)
        e.set_image(url=img_url)
        await ctx.send(embed=e)
        self.prev_search = gallerynumber
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if (not message.guild or message.channel.is_nsfw()) and not message.author.bot and message.content:
            if message.content.lower() == "next":
                await self.hentai(ctx = await self.bot.get_context(message), args = self.last_search)
            if message.content.lower() == "retry":
                await self.nsearch(ctx = await self.bot.get_context(message), args = self.prev_tag)
            if message.content.split()[0] == "favourite" and len(message.content.split()) > 1 and self.last_image:
                await self.favourite(ctx = await self.bot.get_context(message), imageName="".join(message.content.split()[1:]), url=self.last_image)
            elif message.content.split()[0] == "favourite" and len(message.content.split()) > 1:
                await message.channel.send("No previous picture was sent!")
            
            if message.content.lower() == "np":
                ctx = await self.bot.get_context(message)
                self.cur_page += 1
                img_url = 'https://i.nhentai.net/galleries/{gallerynumber}/{page}.'.format(gallerynumber=self.prev_search, page=self.cur_page) + self.extensions[self.cur_page]
                async with aiohttp.ClientSession() as session:
                    async with session.get(img_url) as resp:
                        if resp.status != 200:
                            await ctx.send(
                                'You have reached the end of this work.')
                        else:
                            self.last_image = img_url
                            data = io.BytesIO(await resp.read())
                            await ctx.send(
                                file=discord.File(data, img_url))

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def favourite(self, ctx: commands.Context, imageName: str, url: str = None):
        '''
        Adds an image to the favourites list, or retrieves a favourite based on ID
        '''
        if url:
            updateFavourite(imageName, url, ctx.guild.id, ctx.author.id)
            await reactOK(ctx)
            await ctx.send("Image favourited as `{}`.".format(imageName), delete_after=10)
        else:
            try:
                fav = getFavourite(ctx.guild.id, imageName, ctx.author.id)
                e = discord.Embed()
                e.set_image(url=fav["URL"])
                await ctx.send(embed=e)
            except:
                await delSend(ctx, "Image not found.")

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def unfavourite(self, ctx: commands.Context, imageName: str):
        '''
        removes an image from the favourites list
        '''
        if fav := getFavourite(ctx.guild.id, imageName, ctx.author.id):
            removeFavoruite(ctx.guild.id, imageName, ctx.author.id)
            await reactOK(ctx)
            await ctx.send(f"`{imageName}` has been removed.", delete_after=10)
        else:
            await delSend(ctx, "Image not found.")

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def listfavourites(self, ctx:commands.Context, user: discord.Member = None):
        '''
        Lists all favourited images
        '''

        def constructstring(favs, index):
            '''
            Constructs the string based on array and index.
            '''
            return f"• **[{favs[index]['imageID']}]({favs[index]['URL']})**\n"

        if not user: user = ctx.author

        favs = allFavourites(ctx.guild.id, user.id)

        embeds = [discord.Embed(title=f"All Favourites for {user.display_name} in {ctx.guild}")]

        s, s_prev = "", "" # declare string variables
        
        for i in range(len(favs)):

            if i > 0: s_prev = s
            s += constructstring(favs, i)
            
            try: embeds[-1].set_field_at(0, name="Uncategorized", value=s, inline=False)
            except: embeds[-1].add_field(name="Uncategorized", value=s, inline=False)

            if len(embeds[-1]) > 1024:
                embeds[-1].set_field_at(0, name="Uncategorized", value=s_prev, inline=False) # fall back to previous string set
                embeds.append(discord.Embed(title=f"All Favourites for {user.display_name} in {ctx.guild}"))
                s_prev, s = s, constructstring(favs, i) # rotate strings

        for e in embeds: await ctx.send(embed=e)

    @commands.command()
    @commands.is_nsfw()
    async def hentai(self, ctx: commands.Context, *, args:str = ""):
        '''
        Fetches a number of posts from Danbooru given a series of tags.
        Ex. $c hentai arms_up solo 2

        User $c hentai clear to purge all hentai messages

        Creds to Sunekku on Github
        '''

        # Made by Sunekku
        # Nuha Sahraoui
        # I'm not a hentai addict
        args = args.split()

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
            if "clear" in tag_list:
                setTGT(self.bot.user)
                await ctx.channel.purge(check=purgeCheck, bulk=True)
            else:
                url_base = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1'
                url_base = url_base + '&limit={limit}&tags=-rating%3asafe+sort:random+'.format(
                    limit=limit)
                for i in range(len(tag_list)):
                    url_base = url_base + '{tag}+'.format(tag=tag_list[i])
                    
                try:
                    posts = requests.get(url_base).json()
                except ValueError:
                    await ctx.send(
                        "No results found. Please try another tag.")
                    return

                if len(tag_list) == 0:
                    count = "N/A"
                else:
                    new_tag = tag_list[0]
                    if tag_list[0].endswith('*'):
                        new_tag = tag_list[0][:len(tag_list[0]) - 1]
                    try:
                        num_results = requests.get(
                            'https://gelbooru.com/index.php?page=dapi&s=tag&q=index&json=1&name={tags}'
                            .format(tags=new_tag)).json()
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
                    e = discord.Embed(
                        title=tags,
                        description='ID: {postid}'.format(postid=postid),
                        url=img_url,
                        color=0xfecbed)
                    e.set_author(name='Retrieved from Gelbooru')
                    e.add_field(name='score',
                                value=posts[i]['score'],
                                inline=True)
                    e.add_field(name='rating',
                                value=posts[i]['rating'],
                                inline=True)
                    e.add_field(name='hit count', value=count, inline=True)
                    e.set_footer(text=tag_string)
                    e.set_image(url=img_url)

                    self.last_image = img_url

                    if img_url.endswith(".webm"):
                        async with aiohttp.ClientSession() as session:
                            async with session.get(img_url) as resp:
                                if resp.status != 200:
                                    await ctx.send(
                                        'Could not download file.')
                                else:
                                    data = io.BytesIO(await resp.read())
                                    e.set_thumbnail(
                                        url=
                                        'https://img.icons8.com/cotton/2x/movie-beginning.png'
                                    )
                                    await ctx.send(embed=e)
                                    await ctx.send(
                                        file=discord.File(data, img_url))
                    else:
                        e.set_thumbnail(
                            url=
                            'https://vectorified.com/images/image-gallery-icon-21.png'
                        )
                        await ctx.send(embed=e)
                    
                    s = ""
                    for k in range(len(args)):
                        s = s + args[k] + " "
                    self.last_search = s
            