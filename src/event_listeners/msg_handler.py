import discord
from discord.ext import commands
from utils import *

import random, os

from fuzzywuzzy import fuzz # NOTE: install python-Levenshtein for faster results.

from utils.checks.other_checks import *

class MessageHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def addtrigger(self, ctx:commands.Context, trigger, message):
        '''
        Allows you to make triggers which automatically make 
        '''
        servercfg = DBfind_one(SERVERCFG_COL, {"_id":ctx.guild.id})

        servercfg["message-triggers"][trigger] = message

        DBupdate(SERVERCFG_COL, {"_id":ctx.guild.id}, servercfg)
        await reactOK(ctx)

    async def message_triggers(self, ctx):
        '''
        sends a message into the chat, based on the content of a message
        '''
        PARTIAL_TRIGGERS = {"hello comrade":"henlo", 
                            "cesb":"https://www.youtube.com/watch?v=ON-7v4qnHP8"}

        EXACT_TRIGGERS = DBcfgitem(ctx.guild.id, "message-triggers")

        '''EXACT_TRIGGERS = {"wait.":"https://www.youtube.com/watch?v=sBl9qcaQos4", 
                            "mtc":"https://www.youtube.com/watch?v=bO-NaEj2dQ0", 
                            "i dunno":"https://cdn.discordapp.com/attachments/446457522862161920/745083032532156527/i_dunno.mp4",
                            "approved":"https://cdn.discordapp.com/attachments/446457522862161920/745083256210456657/meme_approved.mp4"}
        '''
        
        try: await delSend(ctx, EXACT_TRIGGERS[ctx.message.content.lower()])
        except:
            for t in PARTIAL_TRIGGERS:
                if t in ctx.message.content.lower(): await delSend(ctx, PARTIAL_TRIGGERS[t])

    async def meme_review(self, message):
        '''
        gets knuckles to review a meme
        '''
        Knuckles_VD = os.listdir("vid")
        
        attach = None
        if len(message.attachments) > 0: attach = message.attachments[0].size # this way, same video gets same hash
        elif len(message.embeds) > 0: attach = message.embeds[0].url
        elif match_url(message.content.lower()): attach = message.content.lower()

        if attach:
            with open(f"vid/{Knuckles_VD[hash(attach) % len(Knuckles_VD)]}", "rb") as f:
                await message.channel.send(file=discord.File(f,"meme review.mp4"))

    @commands.Cog.listener()
    async def on_message(self, message: discord.message):
        if not message.author.bot:

            ctx = await self.bot.get_context(message)

            if jokeMode(ctx) and ctx.guild:
                await self.message_triggers(ctx)

                if fuzz.token_set_ratio(message.content, "still at cb") > 90:
                    await message.channel.send("And that's okay!")

                if "@someone" in message.content.lower():
                    e = discord.Embed(description=random.choice(list(message.guild.members)).mention)
                    e.set_footer(text=f"Random ping by: {message.author.display_name}")
                    await message.channel.send(embed=e)

                    '''
                    echo(await self.bot.get_context(message), random.choice(list(message.guild.members)).mention, str(message.author.id), deleteMsg=False)
                    '''
                
                if message.guild and message.channel.id == DBcfgitem(message.guild.id,"meme-channel"):
                    await self.meme_review(message)
                            
            if not isNotThreat(1)(await self.bot.get_context(message)) and (len(
                    message.attachments) + len(
                    message.embeds) > 0 or match_url(message.content)):
                e = discord.Embed(title="You just posted cringe")
                e.set_image(
                    url=
                    "https://cdn.discordapp.com/attachments/419214713755402262/709165272447057981/unknown-11.png"
                )
                await message.channel.send(embed=e)      