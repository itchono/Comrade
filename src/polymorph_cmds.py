from utils.utilities import *
from utils.mongo_interface import *
from polymorph.text_gen import *
from polymorph.model_gen import *
import time
import ast

'''
POLYMORPH

N-gram based user mimicry tool developed for use with Comrade
'''

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        self.models = {}

        self.localcache = None

        self.defaultload = "the-soviet-union"

        self._last_member = None

        with open("polymorph/{}.dat".format(self.defaultload), "rb") as f:
            cache = pickle.load(f)
            self.localcache = {"cache":cache}

    @commands.command(aliases = ["gen"])
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def polymorph(self, ctx, tgt, number: int = 15):
        '''
        Generates text from model
        '''
        if number > 100 or number < 0:
            await ctx.send("No")
        elif user := await extractUser(self.bot, ctx, tgt):
            c = self.bot.get_cog("Echo")

            if (user.id, ctx.guild.id) in self.models:
                model = self.models[(user.id, ctx.guild.id)]
                await c.echo(ctx, text(model, number), str(user.id), deleteMsg=False)
            else:
                await ctx.send("Model is not yet cached, it will take a bit longer to produce this first iteration of text.")
                await ctx.trigger_typing()
                if model := getmodel(user.id, ctx.guild.id):
                    model = ast.literal_eval((model["model"]))
                    self.models[(user.id, ctx.guild.id)] = model
                    await c.echo(ctx, text(model, number), str(user.id), deleteMsg=False)
                else:
                    await reactX(ctx)
                    await ctx.send("Please build this user first using $c buildmodel {}".format(user.display_name))

    @commands.command()
    async def extractChannel(self, ctx):
        '''
        Extracts all channel data to a list and stores it as a pickle
        '''
        msgs = []

        count = 0

        await ctx.send("Collecting all info for {}. This will take some time.".format(ctx.channel.mention))

        msgs = await ctx.channel.history(limit=None).flatten()

        ex = [{"author":m.author.id, "content":m.content} for m in msgs]

        with open("polymorph/{}.dat".format(ctx.channel.name), "wb") as f:
            pickle.dump(ex, f)
        # backup

        self.localcache = {"cache":ex}

        await ctx.send("File Stored Locally as {}.mdl.".format(ctx.channel.name))

        fillcache(ctx.channel.id, ex)

        await ctx.send("Successfully collected all info for {}.".format(ctx.channel.mention))
    
    @commands.command()
    async def buildmodel(self, ctx, tgt):
        await ctx.trigger_typing()

        if cache := getcache(ctx.channel.id) if not self.localcache else self.localcache:
            if user := await extractUser(self.bot, ctx, tgt):
                t_start = time.perf_counter()

                msgs = [m["content"] for m in cache["cache"] if m["author"] == user.id]

                model = modelfrommsgs(msgs)

                self.models[(user.id, ctx.guild.id)] = model

                fillmodel(user.id, ctx.guild.id, str(model))

                await reactOK(ctx)
                await ctx.send("Model for {} built in {:.3f}s.".format(user.display_name, time.perf_counter()-t_start))
        else:
            await reactX(ctx)
            await ctx.send("Please extract the channel first using $c extractChannel.")
        
    @commands.command()
    async def injectcache(self, ctx, filename=None):
        '''
        Injects dat file into active cache
        '''
        if not filename:
            self.localcache = None
        else:
            with open("polymorph/{}.dat".format(filename), "rb") as f:
                cache = pickle.load(f)
                self.localcache = {"cache":cache}

                await reactOK(ctx)
