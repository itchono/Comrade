from utils.utilities import *
from utils.mongo_interface import *
from polymorph.text_gen import *
from polymorph.model_gen import *

'''
POLYMORPH

N-gram based user mimicry tool developed for use with Comrade
'''

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
        with open("polymorph/Prose Model.mdl", "rb") as f:
            self.modelKZ = pickle.load(f)
        with open("polymorph/Oishee Model.mdl", "rb") as f:
            self.modelOi = pickle.load(f)
        print("Datasets Initialized")

        self._last_member = None


    @commands.command()
    async def genKevin(self, ctx, number: int = 15):
        '''
        Generates text from Kevin Zhao
        '''
        c = self.bot.get_cog("Echo")
        await c.echo(ctx, text(self.modelKZ, number), "268173116474130443", deleteMsg=False)

    @commands.command()
    async def genOishee(self, ctx, number: int = 15):
        '''
        Generates text from Oishee
        '''
        c = self.bot.get_cog("Echo")
        await c.echo(ctx, text(self.modelOi, number), "341736321410400276", deleteMsg=False)