import discord
from discord.ext import commands
from utils import *

import math, typing, string

from PyDictionary import PyDictionary
import html2text
import urllib.request
from bs4 import BeautifulSoup

def isCommand(message: discord.Message):
    '''
    Check's if it's a Comrade Command
    '''
    return BOT_PREFIX in message.content.lower()

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command()
    async def version(self, ctx: commands.Context):
        '''
        Logs version of the bot.
        '''
        await ctx.send("Comrade is running version: {}".format(VERSION))

    @commands.command()
    async def status(self, ctx: commands.Context):
        '''
        Shows the current status of the bot
        '''
        s = "Uptime: {:.2f} s\n".format(time.perf_counter())
        s += "Version: {}\n".format(VERSION)
        s += "Currently connected to {} server(s)\n".format(len(self.bot.guilds))
        s += "Latency: {:.4f}s\n".format(self.bot.latency)
        
        await ctx.send(s)

    @commands.command()
    async def host(self, ctx: commands.Context):
        '''
        Returns name of host machine.
        '''
        await ctx.send("Comrade is currently hosted from: {}. Local time: {}".format(getHost(), localTime().strftime("%I:%M:%S %p %Z")))

    @commands.command()
    @commands.guild_only()
    async def clearcommands(self, ctx:commands.Context):
        '''
        Cleans up commands from sent from users in a channel.
        '''
        await ctx.channel.purge(check=isCommand, bulk=True)

    @commands.group(invoke_without_command=True)
    async def define(self, ctx:commands.Context, *, word):
        '''
        Defines a word
        '''
        if ctx.invoked_subcommand is None:
            await ctx.trigger_typing()

            dictionary=PyDictionary()

            if (meanings := dictionary.meaning(word)):

                printout = f"**__{string.capwords(word)}__:**\n"
     
                for wordtype in meanings:
                    defs = meanings[wordtype]
                    printout += f"__{wordtype}__\n"

                    for num, d in enumerate(defs, 1):
                        printout += f"{num}. {d}\n"

                await ctx.send(printout)
            
            else:
                await delSend(ctx, f"Definition for `{word}` could not be found.")


    @define.command()
    async def urban(self, ctx:commands.Context,*, word):
        '''
        Defines a word in a dictionary

        Credits to MgWg
        '''
        printout = f"**__{string.capwords(word)}__:**\n"

        await ctx.trigger_typing()
            
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers={'User-Agent':user_agent,}
        tags = '%20'.join(word.split(" "))
        url = 'https://www.urbandictionary.com/define.php?term=' + tags
        
        request = urllib.request.Request(url,None,headers)
        try:
            response = urllib.request.urlopen(request)
        except:
            print("No results found.")
            return

        data = response.read()
        soup = BeautifulSoup(data, 'html.parser')
        r = '(?<=<div class\="meaning">)(.*?)(?=<div class\="def-footer">)' #'(?<=href\="/define\.php\?term\='+tags+'" name\=)(.*?)(?=<div class\="def-footer">)'
        num_results = re.findall(r, str(soup))

        h = html2text.HTML2Text()
        h.ignore_links = True

        def_1 = BeautifulSoup(num_results[0], features="html.parser")
        ex = def_1.find_all('div', {'class':'example'})
        example = BeautifulSoup(str(ex[0]), features="html.parser").get_text()
        index = def_1.get_text().index(example)
        def_1 = def_1.get_text()[:index]

        printout += def_1  + f"\n\n__Example:__\n*{example}*"
        await ctx.send(printout)    

    
    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    async def shutdown(self, ctx:commands.Context):
        '''
        Logs out the user.
        '''
        await self.bot.close()
    
    @commands.command(aliases = ["annoy"])
    @commands.check(isNotThreat())
    async def dmUser(self, ctx: commands.Context, user:typing.Union[discord.Member, discord.User]=None, * , message:str):
        '''
        DM given user
        Made by vdoubleu
        '''
        await DM(message, user, discord.Embed(title="", description = f"Sent by: {ctx.author.display_name + f' ({ctx.author}), in {ctx.guild}' if ctx.guild else ctx.author}"))
        await ctx.send(f"DM sent to {user.display_name if ctx.guild else user.name}", delete_after=10)

    @commands.command()
    async def msgInfo(self, ctx: commands.Context, msgid):
        '''
        Gets information about a specific message given an ID.
        '''
        msg = await ctx.channel.fetch_message(msgid)
        await ctx.send("Author: {}".format(msg.author))

    @commands.command()
    async def dateof(self, ctx: commands.Context,*, thing: typing.Union[discord.TextChannel, discord.User, discord.VoiceChannel, discord.Message]):
        '''
        Gets the creation time of a Channel, User, or Message.
        '''
        await ctx.send(f"{thing} was created on {UTCtoLocalTime(thing.created_at).strftime('%B %m %Y at %I:%M:%S %p %Z')}")

    @commands.command()
    async def staleness(self, ctx: commands.Context, channel: discord.TextChannel):
        '''
        Checks when the last message was sent in a channel
        '''
        msg = (await channel.history(limit=1).flatten()).pop()

        t0 = UTCtoLocalTime(msg.created_at)
        difference = (localTime() - t0).days

        await ctx.send(f"Last message in {channel.mention} was sent on {t0.strftime('%B %m %Y at %I:%M:%S %p %Z')} by `{msg.author.display_name}` ({difference} days ago.)")

    @commands.command()
    async def moststale(self, ctx: commands.Context, limit:int = None):
        '''
        Returns the top n most stale channels (default: 15%)
        '''

        channels = {}

        await ctx.trigger_typing()

        for channel in ctx.guild.text_channels:
            try:
                msg = (await channel.history(limit=1).flatten()).pop()

                t0 = UTCtoLocalTime(msg.created_at)
                difference = (localTime() - t0).days

                channels[channel.mention] = difference
            except: pass # empty channel

        if not limit: limit = math.ceil(0.15*len(channels)) # 15% of top

        top = sorted([(channels[k], k) for k in channels], reverse=True)[:limit]

        await ctx.send(f"Top {limit} most stale channels:\n" + "\n".join([f"{top.index(i) + 1}. {i[1]} ({i[0]} days)" for i in top]))

    @commands.command()
    async def news(self, ctx:commands.Context,*, content):
        '''
        Wraps a piece of text in a fancy border for news
        '''
        BORDER_TOP =    "╔═══.·:·.✧    ✦    ✧.·:·.═══╗"
        ACCENT_BORDER = "      ≻───── ⋆✩⋆ ─────≺"
        BORDER_BOTTOM = "╚═══.·:·.✧    ✦    ✧.·:·.═══╝"
        len_border = len(BORDER_TOP)

        words = content.split(" ")
        lines = []
        buffer = "" # line buffer

        while words: # do until the array of words is empty
            
            if len(words[0]) >= len_border and (max_word := words.pop(0)): words = [max_word[:len_border-2] + '-', max_word[len_border-2:]] + words
            # case: word is too long

            while words and len(buffer + words[0]) < len_border: buffer += words.pop(0) + " "
            
            lines.append(buffer.strip(" ").center(len_border)) # center the text in the block after removing spaces
            buffer = ""
                       
        content = "\n".join(lines)

        if ctx.guild:
            c = self.bot.get_cog("Echo")

            # using monospaced font to fix spacing
            await c.extecho(ctx, f"**```{BORDER_TOP}\n{ACCENT_BORDER}\n{content}\n{ACCENT_BORDER}\n{BORDER_BOTTOM}```**", str(ctx.author.id))
        else:
            await ctx.send(f"**```{BORDER_TOP}\n{ACCENT_BORDER}\n{content}\n{ACCENT_BORDER}\n{BORDER_BOTTOM}```**")

    @commands.command()
    @commands.guild_only()
    async def favcolour(self, ctx, member:typing.Optional[discord.Member]=None, colour=None):
        '''
        Sets a user's favourite colour. 
        TODO: Can be either hex or a common word. If recognized, it will show up in your userinfo command.
        can also view another user's favourite colour
        '''
        if member:
            u = DBUser(member.id, ctx.guild.id)
            await ctx.send(f"{member.display_name}'s favourite colour is {u['favourite-colour']}")
        elif colour:
            u = DBUser(ctx.author.id, ctx.guild.id)
            u["favourite-colour"] = colour
            updateDBUser(u)
            await reactOK(ctx)

        else:
            u = DBUser(ctx.author.id, ctx.guild.id)
            await ctx.send(f"{ctx.author.display_name}'s favourite colour is {u['favourite-colour']}")



    



    

