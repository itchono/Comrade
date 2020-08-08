from utils.utilities import *

class Waifu(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def claim(self, ctx:commands.Context,*, waifuname):
        '''
        Claim your favourite waifu :)
        '''
        await ctx.send(f"Congrats {ctx.author.mention}, you claimed **{waifuname}**!")
        