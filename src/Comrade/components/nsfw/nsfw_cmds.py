'''
Hentai.
Credits to Sunekku (Nuha Sahraoui).
'''

import discord
from discord.ext import commands

import aiohttp
import re
import io
import urllib.request
import requests
from bs4 import BeautifulSoup
from random import randrange

from utils.utilities import webscrape_header
from utils.reactions import reactOK
from db import collection


class NSFW(commands.Cog):
    '''
    NSFW Commands
    (Hentai, lewd doujins)
    '''

    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.last_search = ""
        self.cur_page = 0
        self.prev_search = None
        self.extensions = None
        self.prev_tag = ""

    @commands.command()
    @commands.is_nsfw()
    async def nsearch(self, ctx: commands.Context, *, args: str = "small breasts"):
        '''
        Searches for a hentai on nhentai.net
        '''
        tags = re.split(r"\s", args)
        url = 'https://nhentai.net/search/?q='
        for i in range(len(tags)):
            url += (tags[i] + '+')
        request = urllib.request.Request(url, None, webscrape_header)
        try:
            response = urllib.request.urlopen(request)
        except ValueError:
            await ctx.send(
                "No results found. Please try another tag.")
            return

        data = response.read()
        soup = BeautifulSoup(data, 'html.parser')
        num_results = re.findall(r'(?<=/i> ).*?(?= r)', str(soup.h1))[0]
        num_results = re.split(r'\,', num_results)
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
            num_pages = num // 25 + 1
        else:
            num_pages = num // 25
        page = randrange(1, num_pages + 1)
        url2 = url + '&page={page}'.format(page=page)
        request = urllib.request.Request(url2, None, webscrape_header)
        response = urllib.request.urlopen(request)
        data = response.read()
        soup = BeautifulSoup(data, 'html.parser')

        list_nums = []
        for j in range(len(soup.find_all('a'))):
            entry = soup.find_all('a')[j]
            thing = BeautifulSoup(str(entry))

            thing2 = thing.a['href']
            if re.search(r"^/g/\d+", thing2):
                search_number = int(re.findall(r"g/(\d+)/", thing2)[0])
                list_nums.append(search_number)

        search = list_nums[randrange(len(list_nums))]

        await self.nhentai(ctx=ctx, args=search)

        def check(message):
            return message.channel == ctx.channel and \
                message.content in ("next", "favourite") and \
                not message.author.bot

        message = await self.bot.wait_for("message", check=check, timeout=30)

        await self.nsearch(ctx=await self.bot.get_context(message), args=self.prev_tag)

    @commands.command()
    @commands.is_nsfw()
    async def nhentai(self, ctx: commands.Context, args: int = 185217):
        '''
        Fetches a hentai from nhentai.net, by ID.
        '''
        self.cur_page = 0
        url = 'https://nhentai.net/g/{num}/'.format(num=args)
        request = urllib.request.Request(url, None, webscrape_header)
        try:
            response = urllib.request.urlopen(request)
        except BaseException:
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
                y = re.split(r"\.", x)
            imgs.append(y[len(y) - 1])
        self.extensions = imgs

        if araragi_san:
            araragi_san.pop(0)
            value = araragi_san[0]
        else:
            value = "N/A"

        img_url = 'https://t.nhentai.net/galleries/{gallerynumber}/cover.'.format(
            gallerynumber=gallerynumber) + imgs[0]
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


        def check(message):
            return message.channel == ctx.channel and \
                message.content == "np" and \
                not message.author.bot

        message = await self.bot.wait_for("message", check=check, timeout=300)

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



    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @commands.is_nsfw()
    async def favourite(self, ctx: commands.Context, imageName: str, url: str = None):
        '''
        Adds an image to the favourites list

        Category naming system:
        type as `$c favourite category:name <URL>`
        ex. `$c favourite neko:kurumi <URL>` saves an entry under the "neko" category, titled "kurumi

        '''
        if ctx.invoked_subcommand is None:
            if ctx.message.attachments:
                url = ctx.message.attachments[0].url

            tokens = imageName.split(":")  # split tokens

            if len(tokens) > 1:
                collection("favouritensfw").insert_one(
                    {"imageID": tokens[1],
                             "URL": url,
                             "server": ctx.guild.id,
                             "user": ctx.author.id,
                             "category": tokens[0]}
                )
                fullname = f"{tokens[0]}:{tokens[1]}"
            else:

                collection("favouritensfw").insert_one(
                     {"imageID": imageName,
                          "URL": url,
                          "server": ctx.guild.id,
                          "user": ctx.author.id,
                          "category": ""}
                )
                fullname = f"{tokens[0]}"
            await ctx.send(f"Image favourited as `{fullname}`.")


    @favourite.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def view(self, ctx: commands.Context, imageName: str):
        '''
        Retrieves a favourite based on ID
        To view a post, you can either specify a name, category, or both.
        ex. `$c favourite neko:kurumi` or `$c favourite kurumi` will get you identical results,
        UNLESS you have multiple posts under different catergories with the same name, in which case it will be based on the most recent entry.

        You can view other people's favourites by specifying their name when you call the command.
        ex. `$c favourite itchono:neko:kurumi`
        '''
        try:
            tokens = imageName.split(":")  # split tokens

            fav = None

            if len(tokens) == 1:

                if fav := collection(
                    "favouritensfw").find_one({"server": ctx.guild.id,
                                               "imageID": tokens[0],
                                               "user": ctx.author.id,
                                               "category": ""}):
                    pass
                else:
                    fav = collection(
                            "favouritensfw").find_one({
                            "server": ctx.guild.id, "imageID": tokens[0], "user": ctx.author.id})

            elif len(tokens) == 2:

                if fav := collection(
                            "favouritensfw").find_one({"server": ctx.guild.id,
                                        "imageID": tokens[1],
                                            "user": ctx.author.id,
                                            "category": tokens[0]}):
                    pass
                else:
                    member = ctx.guild.get_member(tokens[0])

                    fav = collection(
                    "favouritensfw").find_one({"server": ctx.guild.id, "imageID": tokens[1], "user": member.id})

            elif len(tokens) == 3:

                member = ctx.guild.get_member(tokens[0])

                fav = collection(
                    "favouritensfw").find_one({"server": ctx.guild.id, "imageID": tokens[2], "user": await member.id, "category": tokens[1] if tokens[1] else ""})

            e = discord.Embed()
            e.set_image(url=fav["URL"])
            await ctx.send(embed=e)
        except BaseException:
            await ctx.send("Image not found.")


    @favourite.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def remove(self, ctx: commands.Context, imageName: str):
        '''
        removes an image from the favourites list
        '''
        try:
            tokens = imageName.split(":")  # split tokens

            if len(tokens) > 1:
                collection("favouritensfw").delete_one({"server": ctx.guild.id,
                              "imageID": tokens[1],
                                 "user": ctx.author.id,
                                 "category": tokens[0]})
                fullname = f"{tokens[1]}:{tokens[0]}"
            else:
                collection("favouritensfw").delete_one({"server": ctx.guild.id,
                              "imageID": tokens[0],
                                 "user": ctx.author.id,
                                 "category": ""})
                fullname = f"{tokens[0]}"

            await reactOK(ctx)
            await ctx.send(f"`{fullname}` has been removed.", delete_after=10)

        except BaseException:
            await ctx.send("Image not found.")

    @favourite.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def rename(self, ctx: commands.Context,
                     oldimageName: str, newimageName: str):
        '''
        renames an image in the favourites list
        '''
        tokens = oldimageName.split(":")  # split tokens

        fav = None

        if len(tokens) == 1:
            fav = collection("favouritensfw").find_one({"server": ctx.guild.id,
                              "imageID": tokens[0],
                                 "user": ctx.author.id,
                                 "category": ""})
        elif len(tokens) == 2:
            fav = collection("favouritensfw").find_one({"server": ctx.guild.id,
                              "imageID": tokens[1],
                                 "user": ctx.author.id,
                                 "category": tokens[0]})
        if fav:
            await self.unfavourite(ctx, oldimageName)
            await self.favourite(ctx, newimageName, fav["URL"])

    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def favourites(self, ctx: commands.Context,
                         user: discord.Member = None, category: str = None):
        '''
        Lists all favourited images. Can specify another user, or a category.
        '''
        def construct(fav): return f"• **[{fav['imageID']}]({fav['URL']})**\n"

        if not user:
            user = ctx.author

        if category:
            favs = collection("favouritensfw").find({
                    "server": ctx.guild.id, "user": user.id, "category": category})
        else:
            favs = collection("favouritensfw").find({
                    "server": ctx.guild.id, "user": user.id})

        # Sort favourites by category

        categories = {}

        for fav in favs:
            try:
                categories[fav["category"]].append(fav)
            except BaseException:
                categories[fav["category"]] = [fav]

        embeds = [
            discord.Embed(
                title=f"All Favourites for {user.display_name} in {ctx.guild}")]
        category_count = 0

        for category in categories:
            s, s_prev = "", ""  # declare string variables
            embeds[-1].add_field(name=category if category else "Uncategorized",
                                 value="filler", inline=False)

            for item in categories[category]:
                s_prev = s
                s += construct(item)

                embeds[-1].set_field_at(category_count,
                                        name=embeds[-1].fields[category_count].name,
                                        value=s,
                                        inline=False)

                if len(s) > 1024:

                    embeds[-1].set_field_at(category_count,
                                            name=embeds[-1].fields[category_count].name,
                                            value=s_prev,
                                            inline=False)  # fall back to previous string set

                    if len(embeds[-1]) >= 6000:
                        embeds.append(
                            discord.Embed(
                                title=f"All Favourites for {user.display_name} in {ctx.guild} (cont.)"))
                        category_count = 0

                    else:
                        category_count += 1  # advance count

                    embeds[-1].add_field(
                        name=f'{category if category else "Uncategorized"} (cont.)', value="filler", inline=False)
                    s_prev, s = s, construct(item)  # rotate strings

            category_count += 1

        for e in embeds:
            await ctx.send(embed=e)

    @commands.command()
    @commands.is_nsfw()
    async def hentai(self, ctx: commands.Context, *, args: str = ""):
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
                await ctx.channel.purge(check=lambda m: m.author == self.bot.user, bulk=True)
            else:
                url_base = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1'
                url_base = url_base + \
                    '&limit={limit}&tags=-rating%3asafe+-webm+sort%3arandom+'.format(limit=limit)
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
                    except BaseException:
                        count = "N/A"
                    else:
                        if len(num_results) != 0:
                            count = num_results[0]['count']
                        else:
                            count = 0
                for i in range(len(posts)):
                    img_url = posts[i]['file_url']
                    postid = posts[i]['id']
                    tags = ""
                    for k in range(len(tag_list)):
                        tags += " " + tag_list[k]
                    tag_string = posts[i]['tags']
                    e = discord.Embed(
                        title=tags,
                        description=f'ID: {postid}',
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
                        pass
                        # Abort
                    else:
                        e.set_thumbnail(
                            url='https://vectorified.com/images/image-gallery-icon-21.png')
                        await ctx.send(embed=e)

                    s = ""
                    for k in range(len(args)):
                        s = s + args[k] + " "
                    self.last_search = s

        def check(message):
            return message.channel == ctx.channel and \
                message.content in ("next", "favourite") and \
                not message.author.bot

        message = await self.bot.wait_for("message", check=check, timeout=30)

        # TODO make this a repeatable loop

        if message.content == "next":
            await self.hentai(ctx=await self.bot.get_context(message), args=self.last_search)
        else:
            await self.favourite(ctx=await self.bot.get_context(message), imageName="".join(message.content.split()[1:]), url=self.last_image)

