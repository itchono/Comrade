'''
Fun commands

Fanfic by Kevin Zhao
Fortnite Dance and Text Manipulation by Kevin Hu
Shoujo Commands by Maggie Wang
'''

import discord
from discord.ext import commands

import asyncio
import random
import io
import urllib.request
from bs4 import BeautifulSoup
from PIL import Image

from utils.emoji_converter import emojiToText, textToEmoji
from utils.echo import echo, mimic
from utils.utilities import webscrape_header

# Static dependencies
with open("static/space.txt", "r", encoding="utf-8") as f:
    space = f.read()

with open("static/default_dance.txt", "r", encoding="utf-8") as f:
    default_dance = f.readlines()

with open('static/sparkles.txt', 'r', encoding="utf-8") as sparklesFile:
    sparkles = [s.strip() for s in sparklesFile.readlines()]

with open('static/yukis_feelings.txt', 'r', encoding="utf-8") as kimochiFile:
    thoughts = kimochiFile.read().splitlines()
    # TL Note: kimochi means feeling, but in Japanese


def fortnite_dance():
    '''
    Iterator generator for producing Fortnite Default Dance
    This assumes that the source file separates each dance frame by
    one blank line, and has no blank lines within the dance frames themselves.
    Generalizable to basically any sort of text animation!
    '''
    position = 0
    accum = ""

    while position < len(default_dance):
        if not default_dance[position].strip():
            yield accum
            accum = ""
        else:
            accum += default_dance[position]
        position += 1
    yield accum


def owoify(t):
    '''
    Replaces L, R, with w
    '''
    remove_characters = ["R", "L", "r", "l"]
    for character in remove_characters:
        if character.islower():
            t = t.replace(character, "w")
        else:
            t = t.replace(character, "W")
    return t


def emojify(guild, t):
    '''
    Substitute spaces with emojis from a guild
    '''
    return "".join([str(random.choice(guild.emojis))
                    if s == " " else s for s in t])


def mock(t):
    '''
    Randomly captializes and lowercases letters in string
    '''
    s = ""
    for character in t:
        if random.random() < 0.5:
            s += character.lower()
        else:
            s += character.upper()
    return s


async def shoujosend(ctx: commands.Context, content,
                     file: discord.File = None,
                     embed: discord.Embed = None, tts=False):
    '''
    Send the message, except as a cute anime girl
    '''
    if ctx.guild:
        await ctx.send(content=content, file=file, embed=embed, tts=tts)
    else:
        await mimic(ctx.channel, content=content,
                    username="Yuki Chan",
                    avatar_url="https://cdn.discordapp.com/attachments/420664953435979806/749064831935447071/Annotation_2020-08-24_174359.jpg",
                    file=file, embed=embed, tts=tts)


class Fun(commands.Cog):
    '''
    Fun stuff.
    (Text manipulation, stopping time)
    [Try typing "STAR PLATINUM"]
    '''

    def __init__(self, bot):
        self.bot: commands.Bot = bot

        self.activeGuess = None
        self.guessState = False
        self.streak = {}  # NOTE: Changed to dictionary

    @commands.command()
    async def space(self, ctx: commands.Context):
        '''
        Posts text with stars and space. Best used on dark theme.
        '''
        await ctx.send(space)

    @commands.command()
    async def textToEmoji(self, ctx: commands.Context, *, text):
        '''
        Converts text to emoji
        '''
        await ctx.send(textToEmoji(text))

    @commands.command()
    async def emojiToText(self, ctx: commands.Context, *, text):
        '''
        Converts emoji to text
        '''
        await ctx.send(emojiToText(text))

    @commands.command()
    async def fanfic(self, ctx: commands.Context, *, site):
        '''
        Scrapes text from a webpage with text, and pastes it here
        by Kevinozoid.
        '''
        await ctx.trigger_typing()

        request = urllib.request.Request(site, None, webscrape_header())
        req = urllib.request.urlopen(request)
        html = req.read()
        soup = BeautifulSoup(html, features="html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        holyText = soup.get_text()

        holyText = "\n".join([s for s in holyText.splitlines() if s.strip()])

        if len(holyText) > 10000:
            holyText = holyText[:10000]
            await ctx.send("(Text was trimmed to first 10000 characters for being too long.)")

        paginator = commands.Paginator(prefix="", suffix="")

        lines = holyText.splitlines()

        lines = [lines[i] for i in range(len(lines))]

        for line in lines:
            paginator.add_line(line)

        for page in paginator.pages:
            await ctx.send(page)
            await asyncio.sleep(1)
        await ctx.send("**<END OF TEXT>**")

    @commands.command()
    @commands.guild_only()
    async def timestop(self, ctx: commands.Context, time: int = 5):
        '''
        Stops time.
        '''
        # Make a GIF embed of Jotaro saying "STAR PLATINUM ZA WARUDO"
        embed = discord.Embed(
            title="ZA WARUDO", colour=discord.Colour.purple())
        embed.set_image(url=(
            "https://media1.tenor.com/images/4b953bf5b5ba531099a823944a5626c2/tenor.gif"))

        await ctx.send(embed=embed, delete_after=1.95)

        # Revoke ability for @everyone to send messages
        current_permissions = ctx.channel.overwrites_for(
            ctx.guild.default_role)
        modified_permissions = discord.PermissionOverwrite.from_pair(
            *current_permissions.pair())
        modified_permissions.send_messages = False
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=modified_permissions)

        # Pause while Jotaro gif is playing
        await asyncio.sleep(1.95)

        announcement_msg = await ctx.send("*Time is frozen*")

        # Count the seconds in stopped time, but only if the stop time is less
        # than 20s
        if int(time) <= 20:
            for i in range(int(time)):
                await asyncio.sleep(1)
                t = i + 1
                if t == 1:
                    await announcement_msg.edit(content="1 second has passed", suppress=False)
                else:
                    await announcement_msg.edit(content=f"{t} seconds have passed", suppress=False)
        else:
            await asyncio.sleep(int(time) - 2 if int(time) >= 2 else 0)

        # Restore original permissions
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=current_permissions)

        await announcement_msg.edit(content=f"*Time has begun to move again.*\n(Time stopped by {ctx.author.mention})", suppress=False)
        # await utils.utilities.log(ctx.guild, f"Timestop in
        # {ctx.channel.mention} lasting {time} seconds, performed by
        # {ctx.author.mention}")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        '''
        Emoji call listener
        '''
        if not message.author.bot:
            if message.content.lower()[0:3] == "tte":
                await self.textToEmoji(await self.bot.get_context(message), text=message.content.lower().lstrip("tte "))
            elif message.content.lower()[0:3] == "ett":
                await self.emojiToText(await self.bot.get_context(message), text=message.content.lower().lstrip("ett "))

            if message.guild and message.content == "STAR PLATINUM":
                await self.timestop(await self.bot.get_context(message), 5)

    @commands.command()
    async def defaultdance(self, ctx: commands.Context):
        '''
        Posts Fortnite default dance animation
        '''
        frames = [frame for frame in fortnite_dance()]

        msg = await ctx.send(f"```{frames[0]}```")

        for i in range(1, len(frames)):
            await asyncio.sleep(1)
            await msg.edit(content=f"```{frames[i]}```")

        await asyncio.sleep(10)
        await msg.delete()

    @commands.command(name="owoify")
    async def cmdowoify(self, ctx: commands.Context, *, text: str = ""):
        '''
        changes all R's and L's to W's
        '''
        t = text.strip()

        if len(t) == 0:
            # owoify previous message
            msg = (await ctx.channel.history(limit=2).flatten())[1]
            auth = msg.author
            t = msg.content
        else:
            auth = ctx.author

        if ctx.guild:
            await echo(ctx, member=auth, content=owoify(t))
        else:
            await ctx.send(owoify(t))

    @commands.command(name="emojify")
    @commands.guild_only()
    async def cmdemojify(self, ctx: commands.Context, *, text: str = ""):
        '''
        adds random emojis in spaces
        '''
        t = text.strip()

        if len(t) == 0:
            msg = (await ctx.channel.history(limit=2).flatten())[1]
            auth = msg.author
            t = msg.content
        else:
            auth = ctx.author

        await echo(ctx, member=auth, content=emojify(ctx.guild, t))

    @commands.command(name="mock")
    async def cmdmock(self, ctx: commands.Context, *, text: str = ""):
        '''
        randomly capitalizes and lowercases a message
        '''

        t = text.strip()

        if len(t) == 0:
            msg = (await ctx.channel.history(limit=2).flatten())[1]
            auth = msg.author
            t = msg.content
        else:
            auth = ctx.author

        if ctx.guild:
            await echo(ctx, member=auth, content=mock(t))
        else:
            await ctx.send(mock(t))

    @commands.command()
    @commands.guild_only()
    async def fuckup(self, ctx: commands.Context, *, text: str = ""):
        '''
        Apply every single effect possible to some text
        '''
        t = text.strip()
        if len(t) == 0:
            msg = (await ctx.channel.history(limit=2).flatten())[1]
            auth = msg.author
            t = msg.content
        else:
            auth = ctx.author

        await echo(ctx, member=auth,
                   content=owoify(emojify(ctx.guild, mock(t))))

    @commands.command()
    async def futa(self, ctx: commands.Context, m: discord.Message = None):
        '''
        Developed by Futanari Yaoi.
        Search on Google to learn more about his work
        '''
        if not m:
            m = (await ctx.channel.history(limit=2).flatten())[1]

        # spell futanari yaoi
        await m.add_reaction(u"\U0001F1EB")
        await m.add_reaction(u"\U0001F1FA")
        await m.add_reaction(u"\U0001F1F9")
        await m.add_reaction(u"\U0001F1E6")
        await m.add_reaction(u"\U0001F1F3")
        await m.add_reaction("🅰️")
        await m.add_reaction(u"\U0001F1F7")
        await m.add_reaction(u"\U0001F1EE")

        await m.add_reaction("▪️")

        await m.add_reaction(u"\U0001F1FE")
        await m.add_reaction("4️⃣")
        await m.add_reaction("0️⃣")
        await m.add_reaction("ℹ️")

        await m.add_reaction("◼️")
        await m.add_reaction("♀️")
        await m.add_reaction("♂️")
        await m.add_reaction("🍆")
        await m.add_reaction("💦")

    @commands.command()
    async def ascii(self, ctx: commands.Context, character: str, *, text):
        '''
        Sends a big form of a character in word art form. Can use emojis too.
        '''
        if ctx.guild and (
                e := discord.utils.get(ctx.guild.emojis, name=character)):
            character = str(e)

        letters = {"a": "###\n#b#\n###\n#b#\n#b#",
                   "b": "##b\n#b#\n###\n#b#\n##b",
                   "c": "###\n#bb\n#bb\n#bb\n###",
                   "d": "##b\n#b#\n#b#\n#b#\n##b",
                   "e": "###\n#bb\n###\n#bb\n###",
                   "f": "###\n#bb\n###\n#bb\n#bb",
                   "g": "b##\n#bb\n#b#\n#b#\nb##",
                   "h": "#b#\n#b#\n###\n#b#\n#b#",
                   "i": "###\nb#b\nb#b\nb#b\n###",
                   "j": "###\nb#b\nb#b\nb#b\n#bb",
                   "k": "#bb\n#b#\n#b#\n#b#\n#b#",
                   "l": "#bb\n#bb\n#bb\n#bb\n###",
                   "m": "#b#\n###\n###\n#b#\n#b#",
                   "n": "bbb\nbbb\n##b\n#b#\n#b#",
                   "o": "###\n#b#\n#b#\n#b#\n###",
                   "p": "###\n#b#\n###\n#bb\n#bb",
                   "q": "b#b\n#b#\n#b#\nb##\nbb#",
                   "r": "##b\n#b#\n##b\n#b#\n#b#",
                   "s": "###\n#bb\n###\nbb#\n###",
                   "t": "###\nb#b\nb#b\nb#b\nb#b",
                   "u": "#b#\n#b#\n#b#\n#b#\n###",
                   "v": "#b#\n#b#\n#b#\n#b#\nb#b",
                   "w": "#b#\n#b#\n###\n###\n#b#",
                   "x": "#b#\n#b#\nb#b\n#b#\n#b#",
                   "y": "#b#\n#b#\nb#b\nb#b\nb#b",
                   "z": "###\nbb#\nb#b\n#bb\n###",
                   " ": "bbb\nbbb\nbbb\nbbb\nbbb"}
        try:
            out = ""

            def divide_chunks(l, n):
                for i in range(0, len(l), n):
                    yield l[i:i + n]

            for c in text.lower():
                if c not in letters:
                    raise Exception
                ch = letters[c].replace(
                    "b", ":black_small_square:").replace("#", character)
                out += ch + "\n\n"

            if len(out) > 2000:
                pg = commands.Paginator(prefix="", suffix="")

                for chunk in divide_chunks(out.splitlines(), 6):

                    # start new page if next chunk is too big
                    chunk_length = sum([len(ln) for ln in chunk])

                    if pg.pages and len(pg.pages[-1]) + chunk_length > 2000:
                        pg.close_page()

                    for line in chunk:
                        pg.add_line(line)

                for page in pg.pages:
                    await ctx.send(page)
            else:
                await ctx.send(out)
        except Exception:
            await ctx.send("Text must be alphabetical only.")

    @commands.command()
    async def secret(self, ctx: commands.Context):
        '''
        Sends all your deepest, darkest secrets into a black hole
        '''
        try:
            await ctx.message.delete()
        except Exception:
            pass

        await shoujosend(ctx,
                         content="Don't worry, your secret is safe with me~ (^_<)〜☆")

    @commands.command()
    async def sparklify(self, ctx: commands.Context, *, message=None):
        '''
        makes your message extra kawaii desu~
        functions differently depending on whether you send text or an image
        '''
        feelings = random.choice(thoughts)
        if '{}' in feelings:
            friend = ctx.message.author.display_name

            shoujo_role_exists = 'Shoujotard' in [
                r.name for r in ctx.guild.roles]
            author_has_shoujo_role = shoujo_role_exists and 'Shoujotard' in [
                r.name for r in ctx.author.roles]

            # in the case that the Shoujotard role doesn't exist, call everyone chan
            # Else, only call those who have the Shoujotard role chan
            if (author_has_shoujo_role or not shoujo_role_exists):
                friend += '-chan'
            feelings = feelings.replace('{}', friend)

        if message:
            sparkle = random.choice(sparkles)

            sparklyMessage = f"`{sparkle} {message} {sparkle[-1::-1]}`"

            try:
                await ctx.message.delete()
            except BaseException:
                pass
            await shoujosend(ctx, sparklyMessage)

        else:
            f = io.BytesIO()
            await ctx.message.attachments[0].save(f)
            f.seek(0)
            ogImage = Image.open(f)
            size = max(ogImage.size)

            kiraKira = Image.open("static/sparkle.png").resize((size, size))
            ogImage.paste(kiraKira, (0, 0), kiraKira)

            f.seek(0)
            ogImage.save(f, "PNG")
            f.seek(0)

            await shoujosend(ctx, content=feelings,
                             file=discord.File(f, 'sparklified.png'))
