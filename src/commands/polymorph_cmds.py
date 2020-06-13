from utils.utilities import *
from utils.mongo_interface import *
from polymorph.text_gen import *
from polymorph.model_gen import *
from polymorph.data_compressor import *

import time

'''
POLYMORPH

N-gram based user mimicry tool developed for use with Comrade
'''

class Polymorph(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        self.models = {} # local model store

        self.localcache = None # message cache
        self.localcacheID = None

        self._last_member = None

    @commands.Cog.listener()
    async def on_ready(self):
        '''
        When bot is loaded
        '''
        self.localcache = getcache(DEFAULT_CACHE_LOAD)

        if self.localcache:
            print("Message Cache loaded.")
            self.localcacheID = DEFAULT_CACHE_LOAD
        else:
            print("WARN: Error loading message cache.")

    @commands.command(aliases = ["gen"])
    @commands.guild_only()
    async def polymorph(self, ctx: commands.Context, target: str, number: int = 15):
        '''
        Generates text from model of a user and outputs it to a channel.
        If the model has not yet been built, it builds a model based on the last cached channel.
        If you want the model for a certain channel, run [buildcommand] in that channel.
        '''
        if number > 100 or number < 0: await ctx.send("No")
        
        elif user := await extractUser(ctx, target):
            c = self.bot.get_cog("Echo")

            try:
                model = self.models[(user.id, ctx.guild.id)]
                await c.echo(ctx, text(model, number), str(user.id), deleteMsg=False)

            except:
                await ctx.send("Model is not yet built, it will take a bit longer to produce this first iteration of text.")
                await self.buildmodel(ctx, target, switchchannel=False)
                
                try:
                    model = self.models[(user.id, ctx.guild.id)]
                    await c.echo(ctx, text(model, number), str(user.id), deleteMsg=False)
                except:
                    pass
    
    @commands.command()
    @commands.guild_only()
    async def buildmodel(self, ctx: commands.Context, target: str, switchchannel=True):
        '''
        Builds the n-gram model for a user.
        '''
        await ctx.trigger_typing()

        t_start = time.perf_counter()

        if switchchannel and self.localcacheID != ctx.channel.id:
            # if we need to switchchannel the channel
            await self.switchchannel(ctx, ctx.channel)

        if self.localcache:
            if user := await extractUser(ctx, target):
                
                # check to see if we have too many models cached
                if len(self.models) >= RAM_LIMIT:
                    self.models.pop(list(self.models.keys()).pop())
                    await ctx.send("Model cache full. Freeing up cache...")
                    await ctx.trigger_typing()

                msgs = [m["content"] for m in self.localcache if m["author"] == user.id]
                model = modelfrommsgs(msgs, n=2) # construct 2-gram model

                self.models[(user.id, ctx.guild.id)] = model
                # load model into user cache

                await ctx.send("Model for {} built in {:.3f}s.".format(user.display_name, time.perf_counter()-t_start))
        else:
            await reactX(ctx)
            if not switchchannel: await ctx.send("Model could not be built - no message cache has been loaded. \nUse `{}switchchannel <channel>` to load a channel".format(BOT_PREFIX))
            
            
    @commands.command()
    @commands.guild_only()
    async def switchchannel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        '''
        Changes message cache to the specified channel (current channel by default).
        '''
        await ctx.trigger_typing()
        if not channel: channel = ctx.channel

        self.localcache = getcache(channel.id)
        
        if self.localcache:
            self.localcacheID = channel.id
            await ctx.send("Cache for {} is ready to use.".format(channel.mention))
            
        else:
            self.localcacheID = None
            await ctx.send("Please extract the channel first using `{}extractChannel` in {}".format(BOT_PREFIX, channel.mention))

    @commands.command()
    @commands.guild_only()
    async def extractChannel(self, ctx: commands.Context):
        '''
        Extracts messages in channel and uploads it to MongoDB for use with text generation.
        '''
        msgs = []

        await ctx.send("Collecting all info for {}. This will take some time.".format(ctx.channel.mention))

        msgs = await ctx.channel.history(limit=None).flatten()

        ex = [{"author":m.author.id, "content":m.content} for m in msgs]

        self.localcache = ex
        self.localcacheID = ctx.channel.id

        tx = compressCache(ex, 3)
        fillcache(ctx.channel.id, tx)
        await ctx.send("{} successfully cached and uploaded.".format(ctx.channel.mention))
        await log(ctx.guild, "Channel extracted: {}".format(ctx.channel.mention))
        await reactOK(ctx)

    @commands.command()
    @commands.guild_only()
    async def modelSize(self, ctx: commands.Context):
        '''
        Returns the size of the current model store.
        '''
        await ctx.send("Current storing {} models locally.".format(len(self.models)))

    @commands.command()
    @commands.guild_only()
    async def channelCacheStatus(self, ctx: commands.Context):
        '''
        Returns information about the currently cached channel
        '''
        await ctx.send("Currently loaded cache: {}".format(self.bot.get_channel(self.localcacheID).mention))
  
    @commands.command()
    @commands.check_any(commands.is_owner(), isServerOwner())
    @commands.guild_only()
    async def injectcache(self, ctx: commands.Context, filename=None):
        '''
        Injects .dat file into active cache from local file (in /polymorph directory), or clears it.
        '''
        if not filename:
            self.localcache = None
            await ctx.send("Cache purged.")
        else:
            with open("polymorph/{}.dat".format(filename), "rb") as f:
                self.localcache = pickle.load(f)
                self.localcacheID = "TEST"
            await reactOK(ctx)
