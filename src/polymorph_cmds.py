from utils.utilities import *
from utils.mongo_interface import *
from polymorph.text_gen import *
from polymorph.model_gen import *
from polymorph.data_compressor import *

import time
import ast # dictionary parsing

'''
POLYMORPH

N-gram based user mimicry tool developed for use with Comrade
'''
RAM_LIMIT = 10 # max # of active models


class Polymorph(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        self.models = {}

        self.localcache = None

        self.defaultload = 667245433063735316 # default to channel in my server

        self._last_member = None

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        When bot is loaded
        '''
        self.localcache = getcache(self.defaultload)
        print("Message Cache loaded.")

        # wait nvm we have to do it locally for now

        with open("polymorph/the-soviet-union.dat".format(self.defaultload), "rb") as f:
            self.localcache = pickle.load(f)
            print("Cache loaded.")

    @commands.command(aliases = ["gen"])
    async def polymorph(self, ctx, tgt, number: int = 15):
        '''
        Generates text from model of a user and outputs it to a channel.
        '''
        if number > 100 or number < 0:
            await ctx.send("No")
        elif user := await extractUser(ctx, tgt):
            c = self.bot.get_cog("Echo")

            model = None

            if (user.id, ctx.guild.id) in self.models:
                model = self.models[(user.id, ctx.guild.id)]
                await c.echo(ctx, text(model, number), str(user.id), deleteMsg=False)
            else:
                await ctx.send("Model is not yet built, it will take a bit longer to produce this first iteration of text.")
                await self.buildmodel(ctx, tgt)
                if (user.id, ctx.guild.id) in self.models:
                    model = self.models[(user.id, ctx.guild.id)]
                    await c.echo(ctx, text(model, number), str(user.id), deleteMsg=False)

    @commands.command()
    @commands.check(isOwner)
    async def extractChannel(self, ctx):
        '''
        Extracts all channel data to a list and stores it as a pickle
        '''
        msgs = []

        await ctx.send("Collecting all info for {}. This will take some time.".format(ctx.channel.mention))

        msgs = await ctx.channel.history(limit=None).flatten()

        ex = [{"author":m.author.id, "content":m.content} for m in msgs]

        self.localcache = ex
        self.cachedchannel = ctx.channel.id

        await ctx.send("Successfully collected all info for {}.".format(ctx.channel.mention))

        with open("polymorph/{}.dat".format(ctx.channel.name), "wb") as f:
            pickle.dump(ex, f)
        # backup to local
        
        await ctx.send("File Stored Locally as `{}.dat.`".format(ctx.channel.name))

        await ctx.send("Compressing messages.")
        tx = compressObj(ex, 5)
        fillcache(ctx.channel.id, tx)

        await ctx.send("MongoDB Sync Complete.")

    @commands.command()
    async def modelCacheSize(self, ctx):
        await ctx.send("Current caching {} models locally.".format(len(self.models)))
    
    @commands.command()
    async def buildmodel(self, ctx, tgt=None):
        await ctx.trigger_typing()

        t_start = time.perf_counter()

        if cache := self.localcache:
            if user := await extractUser(ctx, tgt):
                
                if len(self.models) >= RAM_LIMIT:
                    self.models.pop(list(self.models.keys()).pop())
                    await ctx.send("Model cache full. Freeing up cache...")
                    await ctx.trigger_typing()
                msgs = [m["content"] for m in cache if m["author"] == user.id]

                model = modelfrommsgs(msgs, n=2)

                self.models[(user.id, ctx.guild.id)] = model

                await ctx.send("Model for {} built in {:.3f}s.".format(user.display_name, time.perf_counter()-t_start))
        else:
            await reactX(ctx)
            
    @commands.command()
    @commands.check(isOwner) # temporarily; this will work later
    async def recache(self, ctx, channel: discord.TextChannel):
        '''
        Changes gen cache to the current channel
        '''
        self.localcache = getcache(channel.id)
        if self.localcache:
            await reactOK(ctx)
        else:
            await ctx.send("Please extract the channel first using $c extractChannel.")
        
    @commands.command()
    @commands.check(isOwner)
    async def injectcache(self, ctx, filename=None):
        '''
        Injects .dat file into active cache. Use only if you know what you're doing.
        '''
        if not filename:
            self.localcache = None
        else:
            with open("polymorph/{}.dat".format(filename), "rb") as f:
                self.localcache = pickle.load(f)
                await reactOK(ctx)
