from utils.utilities import *
import random

NAMES = ["Apple", "Banana", "Cow", "DNA", "E"]

class Waifu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        self.active_waifu = None

        self.produce_waifu.start()

    @commands.command()
    async def claim(self, ctx:commands.Context,*, waifuname):
        '''
        Claim your favourite waifu :)
        '''
        await ctx.send(f"Congrats {ctx.author.mention}, you claimed **{waifuname}**!")
        
    '''
    Timer based thing
    '''

    @tasks.loop(seconds=5)
    async def produce_waifu(self):

        waifu = random.choice(NAMES)

        self.active_waifu = waifu

        '''iraq_btw = self.bot.get_guild(419214713252216848)

        west_korea = iraq_btw.get_channel(522428899184082945)'''


        # NOTE: This is just for bot development; NOT when we actually deploy
        test_btw = self.bot.get_guild(709954286376976425)
        west_korea = test_btw.get_channel(742181992824700989)

        await west_korea.send(f"Yo a waifu spawned: {waifu}")

    @produce_waifu.before_loop
    async def before(self):
        await self.bot.wait_until_ready()



