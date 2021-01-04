'''
Hentai.
Credits to Sunekku (Nuha Sahraoui).
'''

import discord
from discord.ext import commands
from utils import *

import json, io, aiohttp, re, urllib.request, math, random, requests
from bs4 import BeautifulSoup
from random import randrange
from utils.checks.other_checks import *

class NSFW(commands.Cog):
    '''
    NSFW Commands
    (Hentai, lewd doujins)
    '''
    def __init__(self, bot):
        self.bot = bot
        
        self.last_search = ""
        self.cur_page = 0
        self.prev_search = None
        self.extensions = None
        self.prev_tag = ""

        self.last_image = None
        self.last_tags = None
        self.last_number = None
        self.last_post = None

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
        if random.randint(1,100)<5 and not message.author.bot:
            url_base = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1'
            url_base = url_base + '&tags=-webm+sort%3arandom+'
            post = requests.get(url_base).json()
            self.last_post = post
            img_url = post[0]['file_url']
            self.last_tags = post[0]['tags']
            self.last_number = int(len(post[0]['tags'])/200 + 3)
            e = discord.Embed(description=f":camera_with_flash: **A PNG HAS SPAWNED, NAME {self.last_number} OF ITS TAGS TO CLAIM IT**",
                color=0xfecbed)
            e.set_image(url=img_url)
            list1 = []
            tags = self.last_tags.split()
            for i in range(len(tags)):
                cuts = random.sample(range(len(tags[i])),int(len(tags[i])/2))
                cuttag = ""
                for j in range(len(tags[i])):
                    if j in cuts:
                        cuttag += "_"
                    else:
                        cuttag += tags[i][j]
                list1.append(cuttag)
            e.set_footer(text=" ".join(list1))

            pngchn = await getChannel(message.guild,"png-channel")
            await pngchn.send(embed = e)

    @commands.command(aliases = ["sister"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def favourite(self, ctx: commands.Context, imageName: str, url: str = None):
        '''
        Adds an image to the favourites list, or retrieves a favourite based on ID

        Category naming system:
        type as `$c favourite category:name <URL>`
        ex. `$c favourite neko:kurumi <URL>` saves an entry under the "neko" category, titled "kurumi"
        
        To view a post, you can either specify a name, category, or both.
        ex. `$c favourite neko:kurumi` or `$c favourite kurumi` will get you identical results,
        UNLESS you have multiple posts under different catergories with the same name, in which case it will be based on the most recent entry.

        You can view other people's favourites by specifying their name when you call the command.
        ex. `$c favourite itchono:neko:kurumi`

        '''
        if url or ctx.message.attachments:

            if ctx.message.attachments: url = ctx.message.attachments[0].url

            tokens = imageName.split(":") # split tokens

            if len(tokens) > 1:
                DBupdate(FAVOURITES_COL, {"imageID":tokens[1], "server":ctx.guild.id, "user":ctx.author.id, "category":tokens[0]}, {"imageID":tokens[1], "URL":url, "server":ctx.guild.id, "user":ctx.author.id, "category":tokens[0]})
                fullname = f"{tokens[0]}:{tokens[1]}"
            else:
                DBupdate(FAVOURITES_COL, {"imageID":tokens[0], "server":ctx.guild.id, "user":ctx.author.id, "category":""}, {"imageID":imageName, "URL":url, "server":ctx.guild.id, "user":ctx.author.id, "category":""})
                fullname = f"{tokens[0]}"

            await reactOK(ctx)
            await ctx.send(f"Image favourited as `{fullname}`.")
        else:
            try:
                tokens = imageName.split(":") # split tokens

                fav = None

                if len(tokens) == 1:

                    if fav := DBfind_one(FAVOURITES_COL, {"server":ctx.guild.id, "imageID":tokens[0], "user":ctx.author.id, "category":""}): pass
                    else: fav = DBfind_one(FAVOURITES_COL, {"server":ctx.guild.id, "imageID":tokens[0], "user":ctx.author.id})

                elif len(tokens) == 2:

                    if fav := DBfind_one(FAVOURITES_COL, {"server":ctx.guild.id, "imageID":tokens[1], "user":ctx.author.id, "category":tokens[0]}): pass
                    else: fav = DBfind_one(FAVOURITES_COL, {"server":ctx.guild.id, "imageID":tokens[1], "user":(await getUser(ctx, tokens[0])).id})


                elif len(tokens) == 3:

                    fav = DBfind_one(FAVOURITES_COL, {"server":ctx.guild.id, "imageID":tokens[2], "user":(await getUser(ctx, tokens[0])).id, "category":tokens[1] if tokens[1] else ""})

                
                e = discord.Embed()
                e.set_image(url=fav["URL"])
                await ctx.send(embed=e)
            except:
                await delSend(ctx, "Image not found.")

    @commands.command(aliases = ["turnout"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def unfavourite(self, ctx: commands.Context, imageName: str):
        '''
        removes an image from the favourites list
        '''

        try:
            tokens = imageName.split(":") # split tokens

            if len(tokens) > 1:
                DBremove_one(FAVOURITES_COL, {"server":ctx.guild.id, "imageID":tokens[1], "user":ctx.author.id, "category":tokens[0]})
                fullname = f"{tokens[1]}:{tokens[0]}"
            else:
                DBremove_one(FAVOURITES_COL, {"server":ctx.guild.id, "imageID":tokens[0], "user":ctx.author.id, "category":""})
                fullname = f"{tokens[0]}"

            await reactOK(ctx)
            await ctx.send(f"`{fullname}` has been removed.", delete_after=10)

        except:
            await delSend(ctx, "Image not found.")


    @commands.command()
    @commands.guild_only()
    @commands.is_nsfw()
    async def rename(self, ctx: commands.Context, oldimageName: str, newimageName: str):
        '''
        renames an image in the favourites list
        '''
        tokens = oldimageName.split(":") # split tokens

        fav = None

        if len(tokens) == 1: fav = DBfind_one(FAVOURITES_COL, {"server":ctx.guild.id, "imageID":tokens[0], "user":ctx.author.id, "category":""})
        elif len(tokens) == 2: fav = DBfind_one(FAVOURITES_COL, {"server":ctx.guild.id, "imageID":tokens[1], "user":ctx.author.id, "category":tokens[0]})

        if fav:
            await self.unfavourite(ctx, oldimageName)
            await self.favourite(ctx, newimageName, fav["URL"])


    @commands.command(aliases = ["viewstable"])
    @commands.guild_only()
    @commands.is_nsfw()
    async def favourites(self, ctx:commands.Context, user: discord.Member = None, category:str = None):
        '''
        Lists all favourited images. Can specify another user, or a category.
        '''
        construct = lambda fav:f"• **[{fav['imageID']}]({fav['URL']})**\n"

        if not user: user = ctx.author
       
        if category:
            favs = DBfind(FAVOURITES_COL, {"server":ctx.guild.id, "user":user.id, "category":category})
        else:
            favs = DBfind(FAVOURITES_COL, {"server":ctx.guild.id, "user":user.id})

        # Sort favourites by category

        categories = {}

        for fav in favs:
            try: categories[fav["category"]].append(fav)
            except: categories[fav["category"]] = [fav]

        embeds = [discord.Embed(title=f"All Favourites for {user.display_name} in {ctx.guild}")]
        category_count = 0
        
        for category in categories:
            s, s_prev = "", "" # declare string variables
            embeds[-1].add_field(name=category if category else "Uncategorized", value="filler", inline=False)

            for item in categories[category]:
                s_prev = s
                s += construct(item)
                
                embeds[-1].set_field_at(category_count, name=embeds[-1].fields[category_count].name, value=s, inline=False)

                if len(s) > 1024:

                    embeds[-1].set_field_at(category_count, name=embeds[-1].fields[category_count].name, value=s_prev, inline=False) # fall back to previous string set
                    
                    if len(embeds[-1]) >= 6000:
                        embeds.append(discord.Embed(title=f"All Favourites for {user.display_name} in {ctx.guild} (cont.)"))
                        category_count = 0
                        
                    else: category_count +=1 # advance count

                    embeds[-1].add_field(name=f'{category if category else "Uncategorized"} (cont.)', value="filler", inline=False)
                    s_prev, s = s, construct(item) # rotate strings
            
            category_count += 1
            
        for e in embeds: await ctx.send(embed=e)

    '''@commands.command()
    @commands.is_nsfw()
    async def spawnpng(self, ctx: commands.Context):
        url_base = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1'
        url_base = url_base + '&sort:random+'
        post = requests.get(url_base).json()
        self.last_post = post
        img_url = post[0]['file_url']
        postid = post[0]['id']
        self.last_tags = post[0]['tags']
        self.last_number = int(len(post[0]['tags'])/200 + 3)
        e = discord.Embed(
            title="A PNG HAS SPAWNED, NAME " + str(self.last_number) + " OF ITS TAGS TO CLAIM IT!",
            url=img_url,
            color=0xfecbed)
        e.set_author(name='Retrieved from Gelbooru')
        e.set_image(url=img_url)

        if img_url.endswith(".webm"):
            async with aiohttp.ClientSession() as session:
                async with session.get(img_url) as resp:
                    if resp.status != 200:
                        await ctx.send('Could not download file.')
                    else:
                        data = io.BytesIO(await resp.read())
                        e.set_thumbnail(url='https://img.icons8.com/cotton/2x/movie-beginning.png')
                        await ctx.send(embed=e)
                        await ctx.send(file=discord.File(data, img_url))
        else:
            e.set_thumbnail(url='https://vectorified.com/images/image-gallery-icon-21.png')
            await ctx.send(embed=e)

    @commands.command()
    @commands.is_nsfw()
    async def listtags(self, ctx: commands.Context, *, args:int = ""):
        for i in range(min(len(self.last_tags.split()),args,50)):
            await ctx.send(self.last_tags.split()[i])'''

    @commands.command()
    @commands.is_nsfw()
    async def claimpng(self, ctx: commands.Context, *tags):
        #Claim a png
        claim = True
        user = ctx.author
        if self.last_number and len(tags) >= self.last_number:
            for i in tags:
                if i not in self.last_tags:
                    claim = False
            if claim:
                await ctx.send("Congratulations, you've claimed the last png!")
                DBupdate(PNG_COL, {"imageID": self.last_post[0]['id'], "server":ctx.guild.id, "user":ctx.author.id, "URL":self.last_post[0]['file_url'], "claim_tags":tags, "number":len(DBfind(PNG_COL, {"server":ctx.guild.id, "user":user.id}))}, {"imageID": self.last_post[0]['id'], "server":ctx.guild.id, "user":ctx.author.id,"URL":self.last_post[0]['file_url'], "claim_tags":tags,"number":len(DBfind(PNG_COL, {"server":ctx.guild.id, "user":user.id}))}, True)
                self.last_post = None
                self.last_number = None
                self.last_tags = None
            else:
                await ctx.send("You've got the tags wrong son, try again.")
        else:
            await ctx.send("You're gonna need more tags there son.")

    @commands.command()
    @commands.is_nsfw()
    async def listpngs(self, ctx:commands.Context, *, args:int = 1):
        #List your pngs
        user = ctx.author
        pages = math.ceil(len(DBfind(PNG_COL, {"server":ctx.guild.id, "user":user.id}))/10)
        if 0 < args <= pages:
            construct = lambda pngs:f"{pngs['number']+1}. **[{pngs['imageID']}]({pngs['URL']})**\n"
            s = ""
        
            pngs = DBfind(PNG_COL, {"server":ctx.guild.id, "user":user.id})
            
            terms = ""

            for i in range(len(pngs)-10*args+1,len(pngs)-10*args+11):
                if 0 < i:
                    s = construct(pngs[i-1])
                    terms = s+terms

            e = discord.Embed(
                title = f"Page {args} of {pages} for {user.display_name}'s PNGs in {ctx.guild}", 
                description = terms
            )
            await ctx.send(embed=e)
        else:
            await ctx.send("Please enter a valid page number.")
        
    @commands.command()
    @commands.is_nsfw()
    async def viewpng(self, ctx:commands.Context, args:int = ""):
        #View your pngs
        if 0<args<=len(DBfind(PNG_COL, {"server":ctx.guild.id, "user":ctx.author.id})):
            post = requests.get("https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1&id="+str(DBfind(PNG_COL, {"server":ctx.guild.id, "user":ctx.author.id, "number":(args-1)})[0]['imageID'])).json()
            score = post[0]['score']
            postid = post[0]['id']
            tag_string = post[0]['tags']
            e = discord.Embed(
                            title=str(args),
                            description='ID: {postid}'.format(postid=postid),
                            url=DBfind(PNG_COL, {"server":ctx.guild.id, "user":ctx.author.id, "number":(args-1)})[0]['URL'],
                            color=0xfecbed)
            e.set_author(name='Retrieved from Gelbooru')
            e.add_field(name='score',
                        value=post[0]['score'],
                        inline=True)
            e.add_field(name='rating',
                        value=post[0]['rating'],
                        inline=True)
            e.set_footer(text=tag_string)
            e.set_image(url=DBfind(PNG_COL, {"server":ctx.guild.id, "user":ctx.author.id, "number":(args-1)})[0]['URL'])
            await ctx.send(embed=e)
        else:
            await ctx.send("Please enter a valid PNG number.")

    @commands.command(aliases = ["find"])
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
                await ctx.channel.purge(check=purgeCheck(self.bot.user), bulk=True)
            else:
                url_base = 'https://gelbooru.com/index.php?page=dapi&s=post&q=index&json=1'
                url_base = url_base + '&limit={limit}&tags=-rating%3asafe+-webm+sort%3arandom+'.format(
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
            